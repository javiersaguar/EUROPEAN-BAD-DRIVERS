import numpy as np
import pandas as pd
import pytest

from ebdi.metrics.rates import poisson_interval, rate


def test_rate_is_scale_times_count_over_measured_exposure():
    actual = rate(pd.Series([5, 0]), pd.Series([10_000, 200]))
    assert actual.tolist() == [50.0, 0.0]


def test_missing_and_zero_exposure_are_unranked_not_zero_risk():
    result = rate(pd.Series([4, 4, np.nan]), pd.Series([0, np.nan, 10]))
    assert result.isna().all()


@pytest.mark.parametrize("count,exposure", [([-1], [10]), ([1], [-10])])
def test_negative_inputs_rejected(count, exposure):
    with pytest.raises(ValueError):
        rate(pd.Series(count), pd.Series(exposure))


def test_exact_poisson_zero_count_has_positive_upper_bound():
    low, high = poisson_interval(pd.Series([0, 10]), pd.Series([100_000, 100_000]))
    assert low.iloc[0] == 0
    assert high.iloc[0] == pytest.approx(3.688879454, rel=1e-6)
    assert low.iloc[1] < 10 < high.iloc[1]


def test_missing_exposure_interval_and_invalid_confidence():
    low, high = poisson_interval(pd.Series([2]), pd.Series([0]))
    assert low.isna().all() and high.isna().all()
    with pytest.raises(ValueError):
        poisson_interval(pd.Series([2]), pd.Series([100]), confidence=1)
