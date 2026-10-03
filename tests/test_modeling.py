import numpy as np
import pandas as pd
import pytest

from ebdi.features.severity import (
    CATEGORICAL,
    NUMERIC,
    make_features,
    severity_target,
    temporal_split,
)
from ebdi.modeling.severity import evaluate


def test_features_allowlist_excludes_outcomes_and_unknowns_are_explicit():
    source = pd.DataFrame({c: [1, None] for c in CATEGORICAL})
    source["HORA"], source["MES"] = [0, 23], [1, 12]
    source["TOTAL_MU30DF"], source["TOTAL_HG30DF"] = [0, 1], [0, 0]
    source["TOT_TUR_MU30DF"] = [0, 1]
    actual = make_features(source)
    assert set(actual) == set(CATEGORICAL + NUMERIC)
    assert actual.iloc[1]["COD_PROVINCIA"] == "unknown"
    assert severity_target(source).tolist() == [0, 1]


def test_temporal_holdout_is_disjoint_and_years_cannot_be_missing():
    source = pd.DataFrame({"year": [2024, 2022, 2023]})
    train, valid, test = temporal_split(source)
    assert train.year.tolist() == [2022]
    assert valid.year.tolist() == [2023]
    assert test.year.tolist() == [2024]
    with pytest.raises(ValueError, match="holdout"):
        temporal_split(source.iloc[:2])


def test_evaluation_has_valid_baseline_and_confusion_matrix():
    actual = evaluate(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.4, 0.6, 0.9]))
    assert actual["roc_auc"] == 1
    assert actual["tp"] == 2 and actual["tn"] == 2
    assert actual["precision"] == 1
    with pytest.raises(ValueError):
        evaluate(pd.Series([0, 1]), np.array([0.1, 1.2]))
