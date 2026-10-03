import pandas as pd
import pytest

from ebdi.cleaning.geography import checked_join, normalized_name, province_code


def test_leading_zero_and_alias_reconciliation():
    assert province_code(1) == "01"
    assert normalized_name("Araba/Álava") == normalized_name("Álava")
    assert normalized_name("Balears, Illes") == normalized_name("Balears (Illes)")
    assert normalized_name("Coruña, A") == normalized_name("A Coruña")


@pytest.mark.parametrize("value", [0, 53, 1.5, None])
def test_invalid_province_is_not_silently_coerced(value):
    with pytest.raises((ValueError, TypeError)):
        province_code(value)


def test_join_rejects_missing_year_and_duplicate_denominator():
    left = pd.DataFrame({"province_code": ["01"], "year": [2024]})
    right = pd.DataFrame({"province_code": ["01"], "year": [2023], "exposure": [50]})
    with pytest.raises(ValueError, match="Unmatched"):
        checked_join(left, right, ["province_code", "year"])
    right["year"] = 2024
    with pytest.raises(ValueError, match="Duplicate"):
        checked_join(left, pd.concat([right, right]), ["province_code", "year"])
