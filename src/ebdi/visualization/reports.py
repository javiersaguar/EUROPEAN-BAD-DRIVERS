"""Reproducible figures and findings computed from the real analytical panel."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ebdi.metrics.index import bootstrap_index, composite, sensitivity
from ebdi.utils.io import read_yaml, write_json

COLORS = ["#163b4c", "#cd693e", "#3a8d91", "#d5b662"]
plt.rcParams["svg.hashsalt"] = "ebdi-v0.1"


def save_figure(fig: plt.Figure, path: Path) -> None:
    for ax in fig.axes:
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(colors="#304552", labelsize=9)
    fig.savefig(path.with_suffix(".png"), dpi=220, bbox_inches="tight", facecolor="#fffdf9")
    fig.savefig(
        path.with_suffix(".svg"),
        bbox_inches="tight",
        facecolor="#fffdf9",
        metadata={"Date": None, "Creator": "EBDI | Javier Saguar"},
    )
    svg = path.with_suffix(".svg")
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text(encoding="utf-8").splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def analysis(root: Path) -> dict:
    panel = pd.read_parquet(root / "data/processed/spain_metrics.parquet")
    accidents = pd.read_parquet(root / "data/processed/fact_accidents.parquet")
    europe = pd.read_parquet(root / "data/processed/europe_metrics.parquet")
    config = read_yaml(root / "configs/index_weights.yaml")
    weights, method = config["weights"], config["normalization"]
    minimum = config["minimum_injury_crashes"]
    latest_year = int(panel.year.max())
    from ebdi.visualization.eda import breakdowns, figures

    breakdown = breakdowns(root, accidents)
    figures(root, breakdown, latest_year)
    latest = panel.loc[panel.year.eq(latest_year)].reset_index(drop=True)
    indices = pd.concat(
        [composite(group, weights, method, minimum) for _, group in panel.groupby("year")],
        ignore_index=True,
    )
    indices.to_parquet(root / "data/processed/index.parquet", index=False)
    indices[
        ["province_code", "province", "year", "index_score", "index_rank", "index_eligible"]
    ].to_csv(root / "outputs/tables/index.csv", index=False)
    summary, scenarios = sensitivity(
        latest, weights, method, config["weight_scenarios"], config["random_seed"], minimum
    )
    bootstrap = bootstrap_index(
        accidents.loc[accidents.year.eq(latest_year)],
        latest,
        weights,
        method,
        config["bootstrap_repetitions"],
        config["random_seed"],
        minimum,
    )
    summary = summary.merge(bootstrap, on=["province_code", "province"], validate="one_to_one")
    summary.to_csv(root / "outputs/tables/sensitivity.csv", index=False)
    scenarios.to_csv(root / "outputs/tables/index_scenarios.csv", index=False)
    ranked = indices.pivot(index="province_code", columns="year", values="index_rank")
    rank_stability = ranked.corr(method="spearman")
    rank_stability.to_csv(root / "outputs/tables/year_rank_stability.csv")
    metric_cols = [
        "injury_crashes",
        "injury_crashes_per_100k_population",
        "injury_crashes_per_100k_registered_vehicles",
        "injury_crashes_per_100k_licensed_drivers",
        "fatalities_per_100k_population",
    ]
    correlation = latest[metric_cols].corr(method="spearman")
    correlation.to_csv(root / "outputs/tables/metric_rank_correlations.csv")
    nation = panel.groupby("year", as_index=False)[
        [
            "injury_crashes",
            "fatalities",
            "hospitalized",
            "population",
            "urban_crashes",
            "rear_lateral_crashes",
            "severe_crashes",
            "unknown_collision",
        ]
    ].sum()
    nation["injury_crashes_per_100k_population"] = (
        nation.injury_crashes / nation.population * 100_000
    )
    nation.to_csv(root / "outputs/tables/national_totals.csv", index=False)
    fig_dir = root / "outputs/figures"
    fig_dir.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 16,
            "axes.labelsize": 10,
            "axes.titleweight": "bold",
            "figure.facecolor": "#fffdf9",
            "axes.facecolor": "#fffdf9",
        }
    )
    for metric, name, title in [
        (
            "injury_crashes_per_100k_population",
            "spain_injury_rates",
            "Recorded injury crashes · population denominator",
        ),
        (
            "fatalities_per_100k_population",
            "spain_fatality_rates",
            "Road deaths · a different ranking",
        ),
    ]:
        df = latest.nlargest(15, metric).sort_values(metric)
        fig, ax = plt.subplots(figsize=(10, 7))
        ax.barh(df.province, df[metric], color=COLORS[0])
        error = np.vstack([df[metric] - df[f"{metric}_lower"], df[f"{metric}_upper"] - df[metric]])
        ax.errorbar(
            df[metric], np.arange(len(df)), xerr=error, fmt="none", ecolor=COLORS[1], capsize=3
        )
        ax.set(
            title=f"{title}\nSpain, {latest_year}",
            xlabel="Events per 100,000 residents · conditional Poisson 95% interval",
        )
        fig.text(
            0.12,
            -0.01,
            "Source: DGT + INE 67988. Crash-location burden / resident population; not individual risk.",
            fontsize=8,
        )
        save_figure(fig, fig_dir / name)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(
        latest.injury_crashes_per_100k_population,
        latest.fatalities_per_100k_population,
        s=np.sqrt(latest.injury_crashes) * 2,
        c=COLORS[0],
        alpha=0.7,
    )
    for _, row in latest.nlargest(3, "fatalities_per_100k_population").iterrows():
        ax.annotate(
            row.province,
            (row.injury_crashes_per_100k_population, row.fatalities_per_100k_population),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=8,
        )
    ax.set(
        title=f"Injury burden and fatality burden answer different questions · {latest_year}",
        xlabel="Injury crashes per 100,000 residents",
        ylabel="30-day deaths per 100,000 residents",
    )
    save_figure(fig, fig_dir / "injury_vs_fatality")
    unstable = (
        summary.assign(span=summary.weight_rank_max - summary.weight_rank_min)
        .nlargest(15, "span")
        .sort_values("span")
    )
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.hlines(
        unstable.province, unstable.weight_rank_min, unstable.weight_rank_max, color=COLORS[0], lw=4
    )
    ax.scatter(
        unstable.index_rank, unstable.province, color=COLORS[1], label="Default weights", zorder=3
    )
    ax.set(
        title=f"Where weight choices change the rank most · {latest_year}",
        xlabel="Rank range over 500 Dirichlet weight scenarios (1 = highest score)",
    )
    ax.legend(frameon=False)
    fig.text(
        0.12,
        -0.01,
        "Weight scenario range is methodological sensitivity, not a confidence interval.",
        fontsize=8,
    )
    save_figure(fig, fig_dir / "weight_sensitivity")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(nation.year, nation.injury_crashes_per_100k_population, "o-", color=COLORS[0], lw=2)
    ax.set(
        title="Spanish recorded injury-crash burden · common population denominator",
        ylabel="Injury crashes per 100,000 residents",
        xlabel="Year",
        xticks=nation.year,
    )
    save_figure(fig, fig_dir / "spain_trend")
    eu_latest = europe.loc[europe.year.eq(latest_year)].sort_values(
        "fatalities_per_million_population"
    )
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(
        eu_latest.country,
        eu_latest.fatalities_per_million_population,
        color=[COLORS[1] if code == "ES" else COLORS[0] for code in eu_latest.geo],
    )
    ax.set(
        title=f"EU-27 30-day road fatality burden · {latest_year}",
        xlabel="Fatalities per million residents · country reporting notes apply",
    )
    fig.text(
        0.12,
        -0.01,
        "Source: Eurostat CARE + demo_pjan. Shared outcome definition; population is a proxy for exposure.",
        fontsize=8,
    )
    save_figure(fig, fig_dir / "europe_fatalities")
    fig, ax = plt.subplots(figsize=(7, 6))
    component_corr = latest[list(weights)].corr(method="spearman")
    image = ax.imshow(component_corr, vmin=-1, vmax=1, cmap="RdBu_r")
    short = ["Injury", "Urban", "Rear/lateral", "Fatalities"]
    ax.set(
        xticks=range(len(short)),
        yticks=range(len(short)),
        xticklabels=short,
        yticklabels=short,
        title="Overlapping components can double-count information",
    )
    for i in range(len(short)):
        for j in range(len(short)):
            ax.text(
                j,
                i,
                f"{component_corr.iloc[i, j]:.2f}",
                ha="center",
                va="center",
                color="white"
                if abs(component_corr.to_numpy(dtype=float)[i, j]) > 0.65
                else COLORS[0],
            )
    fig.colorbar(image, ax=ax, label="Spearman correlation")
    save_figure(fig, fig_dir / "component_correlations")
    first_year = int(panel.year.min())
    finding = {
        "years": sorted(int(y) for y in panel.year.unique()),
        "recorded_crashes": len(accidents),
        "latest_year": latest_year,
        "latest_injury_crashes": int(nation.iloc[-1].injury_crashes),
        "latest_fatalities": int(nation.iloc[-1].fatalities),
        "count_vs_population_rank_correlation": float(correlation.to_numpy(dtype=float)[0, 1]),
        "injury_vs_fatality_rank_correlation": float(correlation.to_numpy(dtype=float)[1, -1]),
        "index_rank_stability_first_last": float(rank_stability.to_numpy(dtype=float)[0, -1]),
        "largest_weight_rank_span": float(
            (summary.weight_rank_max - summary.weight_rank_min).max()
        ),
        "largest_injury_population_rate_province": latest.sort_values(
            "injury_crashes_per_100k_population"
        ).iloc[-1]["province"],
        "largest_fatality_population_rate_province": latest.sort_values(
            "fatalities_per_100k_population"
        ).iloc[-1]["province"],
        "weights": weights,
        "normalization": method,
    }
    write_json(root / "outputs/tables/findings.json", finding)
    report = f"""# Findings from the audited release

Generated with `ebdi analysis`. Sources: DGT injury-crash releases 2022–2024 and INE annual census table 67988.

- {finding["recorded_crashes"]:,} recorded injury crashes across three years and 52 provinces.
- In {latest_year}: {finding["latest_injury_crashes"]:,} injury crashes and {finding["latest_fatalities"]:,} deaths at 30 days.
- Raw-count vs population-rate rank correlation: **{finding["count_vs_population_rank_correlation"]:.3f}** (Spearman).
- Injury-rate vs fatality-rate rank correlation: **{finding["injury_vs_fatality_rank_correlation"]:.3f}**.
- Largest injury-crash population rate: **{finding["largest_injury_population_rate_province"]}**;
  largest fatality population rate: **{finding["largest_fatality_population_rate_province"]}**. These are observed territorial burdens.
- Default index rank correlation, {first_year} vs {latest_year}: **{finding["index_rank_stability_first_last"]:.3f}**.
- Maximum rank span across {config["weight_scenarios"]} alternative weight draws: **{finding["largest_weight_rank_span"]:.1f} places**.

These comparisons describe this release, these years and these measured denominators. They do not identify driving ability or causal effects.
Weights and normalization are published in `configs/index_weights.yaml`. Urban and collision-specific metrics overlap with injury crashes;
the correlation figure exposes potential double-counting. Scenario bands measure weight sensitivity, while bootstrap bands measure a separate
hypothetical event-sampling model. Neither covers reporting bias or uncertainty in travel exposure.

See `outputs/tables/` for individual metrics, 24 named method scenarios, random-weight summaries, conditional bootstrap intervals and year stability.
The European chart compares only fatalities using a shared 30-day definition; no cross-country injury/claim composite is supported.
"""
    (root / "docs/findings.md").write_text(report, encoding="utf-8")
    print(report, flush=True)
    return finding
