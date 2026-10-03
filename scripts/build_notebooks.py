"""Execute four small research notebooks against real published results."""

import sys
from pathlib import Path

import nbformat as nbf
from jupyter_client import KernelManager
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
SETUP = """from pathlib import Path
import json
import pandas as pd
from ebdi.metrics.index import composite
from ebdi.utils.io import read_yaml
ROOT = Path.cwd() if (Path.cwd() / "configs").exists() else Path.cwd().parent
TABLES = ROOT / "outputs/tables"
spain = pd.read_csv(TABLES / "spain_metrics.csv", dtype={"province_code": str})
"""

BOOKS = [
    (
        "01_data_audit",
        "Data feasibility and quality",
        [
            (
                "What observations exist?",
                """quality = json.loads((TABLES / "data_quality.json").read_text())
assert quality["status"] == "passed"
print(pd.DataFrame([{k: r[k] for k in ["year", "rows", "fields", "fatalities_30d", "unknown_municipality", "unknown_collision"]} for r in quality["accidents"]]).to_string(index=False))
print("Missing exposures:", quality["missing_exposures"])""",
            ),
            (
                "Does every exposure join have the expected grain?",
                """assert not spain.duplicated(["province_code", "year"]).any()
assert spain.groupby("year").size().eq(52).all()
assert spain.population.gt(0).all()
assert spain.loc[spain.year.eq(2023), ["registered_vehicles", "licensed_drivers"]].isna().all().all()
print("156 unique province-years; 2023 stocks explicitly missing")""",
            ),
            (
                "Country-variable inclusion and actual publisher flags",
                """metadata = pd.read_csv(TABLES / "country_comparability.csv").fillna("")
print(metadata.groupby(["variable", "included"]).size().to_string())
print(metadata.loc[metadata.status_flag.ne(""), ["geo", "year", "variable", "status_flag"]].head(15).to_string(index=False))""",
            ),
        ],
    ),
    (
        "02_spain_eda",
        "Spain: counts, rates and observed crash distributions",
        [
            (
                "National reconciliation",
                """national = pd.read_csv(TABLES / "national_totals.csv")
assert national.injury_crashes.sum() == 301218
print(national.to_string(index=False))""",
            ),
            (
                "Does changing the measure change the territorial ranking?",
                """latest = spain.loc[spain.year.eq(2024)]
columns = ["injury_crashes", "injury_crashes_per_100k_population", "fatalities_per_100k_population"]
print(latest[columns].corr(method="spearman").round(3).to_string())
for column in columns[1:]:
    print(column)
    print(latest.nlargest(5, column)[["province", "injury_crashes", "fatalities", column]].to_string(index=False))""",
            ),
            (
                "When and under what recorded circumstances? Counts are not travel risk",
                """groups = pd.read_csv(TABLES / "crash_breakdowns.csv")
counts = groups.groupby(["year", "dimension"]).injury_crashes.sum().unstack()
assert counts.eq(national.set_index("year").injury_crashes, axis=0).all().all()
print(groups.loc[groups.year.eq(2024) & groups.dimension.eq("TIPO_VIA"), ["label", "injury_crashes", "severe_crashes", "conditional_severe_fraction", "small_sample"]].to_string(index=False))""",
            ),
        ],
    ),
    (
        "03_index_experiments",
        "A transparent index, many methodological choices",
        [
            (
                "Replicate the default and equal-weight alternative",
                """config = read_yaml(ROOT / "configs/index_weights.yaml")
latest = spain.loc[spain.year.eq(2024)]
default = composite(latest, config["weights"], config["normalization"], config["minimum_injury_crashes"])
equal = composite(latest, dict.fromkeys(config["weights"], 1.0))
compare = default[["province", "index_rank"]].rename(columns={"index_rank": "default_rank"})
compare["equal_rank"] = equal.index_rank
compare["change"] = compare.equal_rank - compare.default_rank
print("Weights:", config["weights"])
print(compare.reindex(compare.change.abs().sort_values(ascending=False).index).head(10).to_string(index=False))""",
            ),
            (
                "Weight ranges are scenario sensitivity, not confidence intervals",
                """sensitivity = pd.read_csv(TABLES / "sensitivity.csv")
sensitivity["span"] = sensitivity.weight_rank_max - sensitivity.weight_rank_min
print(sensitivity.nlargest(10, "span")[["province", "index_rank", "weight_rank_min", "weight_rank_max", "bootstrap_rank_lower", "bootstrap_rank_upper"]].to_string(index=False))
assert sensitivity.span.max() == 50
scenarios = pd.read_csv(TABLES / "index_scenarios.csv")
assert len(scenarios.groupby(["scenario", "normalization"])) == 24""",
            ),
            (
                "Year-to-year rank stability is not absolute safety improvement",
                """print(pd.read_csv(TABLES / "year_rank_stability.csv").to_string(index=False))
print("Within-year normalization: compare underlying rates for absolute changes.")""",
            ),
        ],
    ),
    (
        "04_ml_experiments",
        "Severity conditional on a recorded crash",
        [
            (
                "Valid target, selection protocol and negative class",
                """card = json.loads((TABLES / "model_card.json").read_text())
assert card["personal_accident_risk"] is False
print(card["target"])
print(card["selection_criterion"])
print("Predictors:", card["features"])
print(pd.read_csv(TABLES / "model_validation.csv").to_string(index=False))""",
            ),
            (
                "Untouched 2024 evaluation: compare all three candidates",
                """metrics = pd.read_csv(TABLES / "model_metrics.csv")
assert metrics.n.eq(101996).all()
assert metrics.positive_n.eq(10019).all()
print(metrics.to_string(index=False))
print("Low recall at the fixed 0.5 threshold prevents interpreting AUC as screening performance.")""",
            ),
            (
                "Calibration has bin sample sizes; attribution is not causal",
                """print(pd.read_csv(TABLES / "model_calibration.csv").to_string(index=False))
print(pd.read_csv(TABLES / "model_permutation_importance.csv").head(8).to_string(index=False))
if (TABLES / "model_shap.json").exists():
    shap = json.loads((TABLES / "model_shap.json").read_text())
    assert shap["maximum_additivity_error"] < 1e-5
    assert not shap["causal_interpretation"]
    print(shap)
    print(pd.read_csv(TABLES / "model_shap_importance.csv").head(8).to_string(index=False))""",
            ),
        ],
    ),
]


def main() -> None:
    directory = ROOT / "notebooks"
    directory.mkdir(exist_ok=True)
    for name, title, sections in BOOKS:
        notebook = nbf.v4.new_notebook()
        notebook.metadata.kernelspec = {
            "display_name": "Python 3 (EBDI)",
            "language": "python",
            "name": "python3",
        }
        notebook.metadata.language_info = {"name": "python", "version": "3.12"}
        notebook.cells = [
            nbf.v4.new_markdown_cell(
                f"# {title}\n\nReal published results from DGT, INE and Eurostat. Author: Javier Saguar.\n\nSee [methodology](../docs/methodology.md), [sources](../docs/sources.md) and [limitations](../docs/limitations.md).\n\nReusable implementations live in `src/`; reproduce artifacts using the CLI before rerunning these explorations."
            ),
            nbf.v4.new_code_cell(SETUP),
        ]
        for heading, code in sections:
            notebook.cells.extend(
                [nbf.v4.new_markdown_cell(f"## {heading}"), nbf.v4.new_code_cell(code)]
            )
        manager = KernelManager(kernel_name="python3")
        manager.kernel_spec.argv = [
            sys.executable,
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ]
        try:
            NotebookClient(
                notebook, km=manager, timeout=120, resources={"metadata": {"path": str(directory)}}
            ).execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
        nbf.validate(notebook)
        nbf.write(notebook, directory / f"{name}.ipynb")
        print(f"Executed: {name}", flush=True)


if __name__ == "__main__":
    main()
