import numpy as np
import pandas as pd
import pytest

from ebdi.metrics.index import composite, normalize, sensitivity, validate_weights


def frame():
    return pd.DataFrame(
        {
            "province_code": ["01", "02", "03"],
            "province": ["A", "B", "C"],
            "injury_crashes": [50, 60, 5],
            "a": [1, 9, 100],
            "b": [9, 1, np.nan],
        }
    )


@pytest.mark.parametrize("method", ["zscore", "robust_zscore", "minmax", "percentile"])
def test_normalizations_preserve_order_and_missingness(method):
    values = normalize(pd.Series([1.0, 2.0, 8.0, np.nan]), method)
    assert values.iloc[0] < values.iloc[1] < values.iloc[2]
    assert pd.isna(values.iloc[3])


def test_constant_component_is_neutral_not_division_by_zero():
    assert normalize(pd.Series([2, 2]), "percentile").tolist() == [50, 50]
    assert normalize(pd.Series([2, 2]), "robust_zscore").tolist() == [0, 0]


@pytest.mark.parametrize("weights", [{}, {"a": 0}, {"a": -1}, {"a": np.nan}, {"a": np.inf}])
def test_invalid_weights_rejected(weights):
    with pytest.raises(ValueError):
        validate_weights(weights)


def test_missing_active_components_and_small_groups_are_not_ranked():
    actual = composite(frame(), {"a": 3, "b": 1})
    assert actual.index_score.iloc[:2].tolist() == [25, 75]
    assert not actual.index_eligible.iloc[2]
    assert pd.isna(actual.index_rank.iloc[2])


def test_zero_weight_component_does_not_require_its_missing_values():
    actual = composite(frame(), {"a": 1, "b": 0}, minimum=0)
    assert actual.index_eligible.all()
    with pytest.raises(ValueError, match="Unknown"):
        composite(frame(), {"invented": 1})


def test_weight_changes_reverse_a_ranking_and_sensitivity_is_reproducible():
    data = frame().iloc[:2]
    assert composite(data, {"a": 1}).index_rank.tolist() == [2, 1]
    assert composite(data, {"b": 1}).index_rank.tolist() == [1, 2]
    a, details = sensitivity(data, {"a": 0.5, "b": 0.5}, scenarios=20)
    b, _ = sensitivity(data, {"a": 0.5, "b": 0.5}, scenarios=20)
    pd.testing.assert_frame_equal(a, b)
    assert set(details.normalization) == {"percentile", "zscore", "robust_zscore", "minmax"}
