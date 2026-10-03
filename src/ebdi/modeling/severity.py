"""Temporal comparison of recorded injury-crash severity models, never personal risk."""

import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    log_loss,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from ebdi.features.severity import (
    CATEGORICAL,
    NUMERIC,
    make_features,
    severity_target,
    temporal_split,
)
from ebdi.utils.io import write_json
from ebdi.visualization.reports import save_figure


def evaluate(
    y: pd.Series, probability: np.ndarray, threshold: float = 0.5
) -> dict[str, float | int]:
    if (
        not 0 <= threshold <= 1
        or not np.isfinite(probability).all()
        or (probability < 0).any()
        or (probability > 1).any()
    ):
        raise ValueError("Probabilities and threshold must lie in [0,1]")
    prediction = probability >= threshold
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {
        "n": len(y),
        "positive_n": int(y.sum()),
        "prevalence": float(y.mean()),
        "roc_auc": float(roc_auc_score(y, probability)),
        "pr_auc": float(average_precision_score(y, probability)),
        "log_loss": float(log_loss(y, probability, labels=[0, 1])),
        "brier": float(brier_score_loss(y, probability)),
        "threshold": threshold,
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def calibration_table(y: pd.Series, probability: np.ndarray, name: str) -> pd.DataFrame:
    frame = pd.DataFrame({"y": y.to_numpy(), "probability": probability})
    frame["bin"] = pd.cut(frame.probability, np.linspace(0, 1, 11).tolist(), include_lowest=True)
    result = (
        frame.groupby("bin", observed=True)
        .agg(
            mean_prediction=("probability", "mean"),
            observed_frequency=("y", "mean"),
            n=("y", "size"),
        )
        .reset_index(drop=True)
    )
    result["model"] = name
    return result


def models() -> dict[str, Pipeline]:
    def preprocess(sparse: bool) -> ColumnTransformer:
        return ColumnTransformer(
            [
                (
                    "codes",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=sparse),
                    CATEGORICAL,
                ),
                ("time", StandardScaler(), NUMERIC),
            ],
            sparse_threshold=1.0 if sparse else 0.0,
        )

    return {
        "dummy": Pipeline(
            [("features", preprocess(True)), ("model", DummyClassifier(strategy="prior"))]
        ),
        "logistic": Pipeline(
            [
                ("features", preprocess(True)),
                ("model", LogisticRegression(max_iter=500, C=1.0, random_state=42)),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("features", preprocess(False)),
                (
                    "model",
                    HistGradientBoostingClassifier(
                        max_iter=120,
                        max_leaf_nodes=15,
                        learning_rate=0.08,
                        l2_regularization=1,
                        early_stopping=False,
                        random_state=42,
                    ),
                ),
            ]
        ),
    }


def train(root: Path) -> dict[str, Any]:
    frame = pd.read_parquet(root / "data/processed/fact_accidents.parquet")
    earlier, validation, test = temporal_split(frame)
    x_train, x_validation, x_test = map(make_features, [earlier, validation, test])
    y_train, y_validation, y_test = map(severity_target, [earlier, validation, test])
    candidates = models()
    validation_rows = []
    for name, estimator in candidates.items():
        print(f"Training {name} on {len(earlier):,} crashes...", flush=True)
        estimator.fit(x_train, y_train)
        probability = estimator.predict_proba(x_validation)[:, 1]
        validation_rows.append(
            {"model": name, "split": "validation_2023", **evaluate(y_validation, probability)}
        )
    chosen = str(min(validation_rows, key=lambda row: row["log_loss"])["model"])
    # Selection and threshold are frozen before inspecting the final holdout.
    train_validation = pd.concat([earlier, validation], ignore_index=True)
    x_combined, y_combined = make_features(train_validation), severity_target(train_validation)
    rows: list[dict[str, Any]] = []
    calibrations: list[pd.DataFrame] = []
    prediction_by_model: dict[str, np.ndarray] = {}
    pr_data: list[dict[str, Any]] = []
    for name, estimator in candidates.items():
        print(f"Refitting {name} on 2022–2023; evaluating 2024...", flush=True)
        estimator.fit(x_combined, y_combined)
        probability = estimator.predict_proba(x_test)[:, 1]
        prediction_by_model[name] = probability
        rows.append(
            {
                "model": name,
                "split": "test_2024",
                "selected_on_validation": name == chosen,
                **evaluate(y_test, probability),
            }
        )
        calibrations.append(calibration_table(y_test, probability, name))
        precision, recall, _ = precision_recall_curve(y_test, probability)
        positions = np.unique(
            np.linspace(0, len(precision) - 1, min(200, len(precision))).astype(int)
        )
        pr_data.extend(
            {"model": name, "precision": float(precision[i]), "recall": float(recall[i])}
            for i in positions
        )
    metrics = pd.DataFrame(rows)
    calibration = pd.concat(calibrations, ignore_index=True)
    metrics.to_csv(root / "outputs/tables/model_metrics.csv", index=False)
    pd.DataFrame(validation_rows).to_csv(root / "outputs/tables/model_validation.csv", index=False)
    calibration.to_csv(root / "outputs/tables/model_calibration.csv", index=False)
    pd.DataFrame(pr_data).to_csv(root / "outputs/tables/model_pr_curve.csv", index=False)
    winner = candidates[chosen]
    sample = x_test.sample(n=min(5000, len(x_test)), random_state=42)
    print(
        "Measuring holdout permutation importance on a reproducible 5,000-row sample...", flush=True
    )
    perm = permutation_importance(
        winner,
        sample,
        y_test.loc[sample.index],
        scoring="neg_log_loss",
        n_repeats=3,
        random_state=42,
        n_jobs=1,
    )
    importance = pd.DataFrame(
        {
            "feature": sample.columns,
            "importance_log_loss_increase": perm.importances_mean,
            "std": perm.importances_std,
        }
    ).sort_values("importance_log_loss_increase", ascending=False)
    importance.to_csv(root / "outputs/tables/model_permutation_importance.csv", index=False)
    model_dir = root / "outputs/models"
    model_dir.mkdir(exist_ok=True)
    joblib.dump(winner, model_dir / "conditional_severity.joblib")
    result = {
        "target": "Recorded injury crash has >=1 fatality or hospitalized injury at 30 days",
        "personal_accident_risk": False,
        "train_year": 2022,
        "validation_year": 2023,
        "test_year": 2024,
        "refit_years": [2022, 2023],
        "selected_model": chosen,
        "selection_criterion": "2023 validation log loss; 2024 never used for model selection",
        "threshold": 0.5,
        "threshold_policy": "fixed in advance; not tuned using test labels",
        "features": list(x_combined.columns),
        "test_metrics": metrics.to_dict("records"),
        "source_hashes": [
            {"id": r["id"], "sha256": r["sha256"]}
            for r in json.loads((root / "data/raw/manifest.json").read_text(encoding="utf-8"))
            if "accidents" in r["id"]
        ],
        "notes": "Descriptive conditional severity; reporting and outcome-based selection limit generalization. Permutation importance is association, not causal influence.",
    }
    write_json(root / "outputs/tables/model_card.json", result)
    colors = ["#9eaaa9", "#cd693e", "#163b4c"]
    fig, ax = plt.subplots(figsize=(8, 6))
    for (model_name, group), color in zip(
        calibration.groupby("model", sort=False), colors, strict=True
    ):
        ax.plot(
            group.mean_prediction,
            group.observed_frequency,
            "o-",
            label=str(model_name),
            color=color,
        )
    ax.plot([0, 1], [0, 1], "--", c="#b0b8b5", label="Perfect calibration")
    ax.set(
        title="Conditional crash severity · untouched 2024 holdout",
        xlabel="Mean predicted severity frequency",
        ylabel="Observed severe-crash frequency",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    ax.legend(frameon=False)
    save_figure(fig, root / "outputs/figures/model_calibration")
    fig, ax = plt.subplots(figsize=(9, 6))
    top = importance.head(10).sort_values("importance_log_loss_increase")
    ax.barh(top.feature, top.importance_log_loss_increase, xerr=top["std"], color="#163b4c")
    ax.set(
        title="Predictive association · held-out permutation importance",
        xlabel="Increase in log loss after permuting one feature (± repetition SD)",
    )
    save_figure(fig, root / "outputs/figures/model_importance")
    selected_metrics = metrics.loc[metrics.model.eq(chosen)].iloc[0]
    card = f"""# Conditional-severity model card

**Target:** whether a recorded injury crash includes a fatality or hospitalized injured person at 30 days.
**This is not P(accident | person) and not personal annual risk.**

Training: 2022 ({len(earlier):,} records); validation: 2023 ({len(validation):,}); test: 2024 ({len(test):,}).
Select by validation log loss, then refit on 2022–2023. The holdout is untouched during model and threshold selection.
Selected model: `{chosen}`. Test ROC-AUC {selected_metrics.roc_auc:.3f}, PR-AUC {selected_metrics.pr_auc:.3f},
log loss {selected_metrics.log_loss:.4f}, Brier score {selected_metrics.brier:.4f}.
All candidate results, prevalence, sample sizes and confusion matrices are in `outputs/tables/model_metrics.csv`.

The three baselines are a prior-frequency dummy, logistic regression and histogram gradient boosting.
Boosting is tested against simpler baselines without adding a heavyweight XGBoost dependency. There is no hyperparameter
search on 2024. A fixed 0.5 threshold is reported for completeness; it is not an operational recommendation.

Predictors: recorded province, urban/interurban environment, road and collision type, junction, weather, lighting,
surface, weekday and cyclic hour/month encodings. No victim totals, fatality-by-category counts, IDs or outcome-derived
variables are predictors. Unknown codes remain explicit categories. Driver demographics and vehicle ages do not exist here.
Some attributes are recorded or reconstructed after the crash; this is a descriptive research model, not a live forecast.

Explainability uses reproducible holdout permutation importance (5,000 rows; three repeats), with standard deviations.
Correlated predictors can dilute importance. Calibration bins include sample sizes; sparse bins are unstable.
Optional TreeSHAP explains a seeded 400-row 2024 sample in raw log-odds. Run `uv run --extra explain ebdi explain`;
the explanation command verifies additivity against the fitted model and publishes a beeswarm, grouped importance
and metadata. Tree-path-dependent attributions depend on the fitted representation and correlated predictors;
they do not identify causal effects. SHAP is an optional dependency so the core pipeline stays smaller.
No causal claim, personalized insurance recommendation or real-world individual risk calculator is supported.

The fitted model is saved locally to `outputs/models/conditional_severity.joblib` with source hashes in the JSON model card.
Do not load untrusted pickle/joblib files. Git excludes model binaries; regenerate with `uv run ebdi model`.
"""
    (root / "docs/model_card.md").write_text(card, encoding="utf-8")
    print(metrics.to_string(index=False), flush=True)
    return result
