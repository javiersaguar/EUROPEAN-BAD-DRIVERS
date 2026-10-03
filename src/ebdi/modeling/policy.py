"""Exploratory threshold study: 2022 fit, F2 chosen only on 2023, 2024 report.

2024 has already been inspected in the original release, so this extension is
explicitly exploratory. A new future holdout is required for confirmation.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve

from ebdi.features.severity import make_features, severity_target, temporal_split
from ebdi.modeling.severity import evaluate, models
from ebdi.utils.io import write_json


def choose_f2_threshold(y: pd.Series, probabilities: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y, probabilities)
    if not len(thresholds):
        raise ValueError("No thresholds available")
    denominator = 4 * precision[:-1] + recall[:-1]
    f2 = np.divide(
        5 * precision[:-1] * recall[:-1],
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0,
    )
    return float(thresholds[np.argmax(f2)])


def evaluate_policy(root: Path) -> dict:
    frame = pd.read_parquet(root / "data/processed/fact_accidents.parquet")
    train, validation, test = temporal_split(frame)
    name = json.loads((root / "outputs/tables/model_card.json").read_text())["selected_model"]
    model = models()[name]
    model.fit(make_features(train), severity_target(train))
    validation_probability = model.predict_proba(make_features(validation))[:, 1]
    threshold = choose_f2_threshold(severity_target(validation), validation_probability)
    test_probability = model.predict_proba(make_features(test))[:, 1]
    rows = [
        {
            "policy": policy,
            "model": name,
            "train_year": 2022,
            "threshold_selection_year": 2023,
            "evaluation_year": 2024,
            **evaluate(severity_target(test), test_probability, cutoff),
        }
        for policy, cutoff in [("fixed_0.5", 0.5), ("validation_F2", threshold)]
    ]
    pd.DataFrame(rows).to_csv(root / "outputs/tables/model_policy.csv", index=False)
    precision, recall, cutoffs = precision_recall_curve(
        severity_target(validation), validation_probability
    )
    positions = np.unique(np.linspace(0, len(cutoffs) - 1, min(200, len(cutoffs))).astype(int))
    pd.DataFrame(
        {
            "threshold": cutoffs[positions],
            "precision": precision[positions],
            "recall": recall[positions],
        }
    ).to_csv(root / "outputs/tables/model_validation_thresholds.csv", index=False)
    report = {
        "model": name,
        "fit_year": 2022,
        "threshold_selection_year": 2023,
        "reported_year": 2024,
        "selection_objective": "maximize F2 on validation (recall weighted 4x precision in harmonic denominator)",
        "selected_threshold": threshold,
        "confirmatory": False,
        "future_holdout_required": True,
        "notes": "Exploratory extension after original 2024 results were inspected. No test labels used to choose this threshold. Same 2022-fitted model for both policies; not the refitted original model. Conditional recorded-crash severity, no personal accident probability.",
    }
    write_json(root / "outputs/tables/model_policy.json", report)
    return report
