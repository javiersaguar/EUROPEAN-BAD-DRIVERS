"""Optional SHAP attribution on a reproducible held-out sample."""

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ebdi.features.severity import CATEGORICAL, NUMERIC, make_features
from ebdi.utils.io import write_json
from ebdi.visualization.reports import save_figure


def explain(root: Path) -> dict:
    try:
        import shap
    except ImportError as import_error:
        raise RuntimeError(
            "Install the explanation extra: uv sync --extra explain; then uv run --extra explain ebdi explain"
        ) from import_error
    fitted = joblib.load(root / "outputs/models/conditional_severity.joblib")
    card = json.loads((root / "outputs/tables/model_card.json").read_text(encoding="utf-8"))
    data = pd.read_parquet(root / "data/processed/fact_accidents.parquet")
    sample = make_features(data.loc[data.year.eq(2024)].sample(400, random_state=42))
    transformed = fitted.named_steps["features"].transform(sample)
    matrix = transformed.toarray() if hasattr(transformed, "toarray") else transformed
    names = fitted.named_steps["features"].get_feature_names_out().tolist()
    classifier = fitted.named_steps["model"]
    if card["selected_model"] == "hist_gradient_boosting":
        explainer = shap.TreeExplainer(
            classifier,
            feature_perturbation="tree_path_dependent",
            model_output="raw",
            feature_names=names,
        )
    elif card["selected_model"] == "logistic":
        background = make_features(data.loc[data.year.le(2023)].sample(100, random_state=42))
        background = fitted.named_steps["features"].transform(background)
        background = background.toarray() if hasattr(background, "toarray") else background
        explainer = shap.LinearExplainer(classifier, background, feature_names=names)
    else:
        raise ValueError("Dummy selected: no feature-based attribution exists")
    print("Computing SHAP on 400 held-out crashes...", flush=True)
    explanation = explainer(matrix)
    reconstructed = np.asarray(explanation.base_values) + np.asarray(explanation.values).sum(axis=1)
    expected = classifier.decision_function(matrix)
    error = float(np.max(np.abs(reconstructed - expected)))
    if error > 1e-5:
        raise ValueError(f"SHAP additivity check failed: {error}")
    shap.summary_plot(
        explanation.values,
        matrix,
        feature_names=names,
        max_display=18,
        show=False,
        plot_size=(10, 8),
        rng=np.random.default_rng(42),
    )
    plt.title("Conditional severity · SHAP association in log-odds", fontsize=14)
    save_figure(plt.gcf(), root / "outputs/figures/model_shap_summary")
    grouped = []
    for original in [*CATEGORICAL, *NUMERIC]:
        matching = [
            i
            for i, name in enumerate(names)
            if name == f"time__{original}" or name.startswith(f"codes__{original}_")
        ]
        attribution = explanation.values[:, matching].sum(axis=1)
        grouped.append(
            {"feature": original, "mean_absolute_shap_log_odds": float(np.abs(attribution).mean())}
        )
    pd.DataFrame(grouped).sort_values("mean_absolute_shap_log_odds", ascending=False).to_csv(
        root / "outputs/tables/model_shap_importance.csv", index=False
    )
    metadata = {
        "model": card["selected_model"],
        "sample_year": 2024,
        "sample_n": 400,
        "seed": 42,
        "output": "raw log-odds of recorded-crash severity",
        "maximum_additivity_error": error,
        "causal_interpretation": False,
        "dependence_assumption": "tree-path-dependent for boosting; training background for logistic",
    }
    write_json(root / "outputs/tables/model_shap.json", metadata)
    print(metadata, flush=True)
    return metadata
