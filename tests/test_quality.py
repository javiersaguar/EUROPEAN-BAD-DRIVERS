import pandas as pd
import pytest

from ebdi.validation import quality


@pytest.fixture
def source(monkeypatch):
    # Small invented records are test fixtures only, never published analytical data.
    monkeypatch.setitem(quality.BASELINE_ROWS, 2024, 2)
    monkeypatch.setitem(quality.BASELINE_DEATHS, 2024, 1)
    df = pd.DataFrame(
        {
            "ID_ACCIDENTE": [1, 2],
            "ANYO": [2024, 2024],
            "MES": [1, 12],
            "DIA_SEMANA": [1, 7],
            "HORA": [0, 23],
            "COD_PROVINCIA": [1, 52],
            "COD_MUNICIPIO": [0, 10],
            "ZONA_AGRUPADA": [1, 2],
            "TIPO_ACCIDENTE": [4, None],
            "TOTAL_MU30DF": [1, 0],
            "TOTAL_HG30DF": [0, 1],
            "TOTAL_HL30DF": [0, 1],
            "TOTAL_VICTIMAS_30DF": [1, 2],
            "TOTAL_VEHICULOS": [1, 2],
        }
    )
    return df, list(df.columns)


def test_optional_collision_missingness_is_reported(source):
    df, schema = source
    report = quality.validate_accidents(df, 2024, schema, {"TIPO_ACCIDENTE": {4}})
    assert report["unknown_collision"] == 1
    assert report["unknown_municipality"] == 1


@pytest.mark.parametrize(
    "column,value,match",
    [
        ("ID_ACCIDENTE", None, "null"),
        ("ANYO", 2023, "mapping"),
        ("TOTAL_MU30DF", -1, "counts"),
        ("HORA", 24, "HORA"),
        ("COD_PROVINCIA", 53, "PROVINCIA"),
        ("TOTAL_VICTIMAS_30DF", 20, "totals"),
        ("TIPO_ACCIDENTE", 1000, "category drift"),
    ],
)
def test_invalid_source_facts_rejected(source, column, value, match):
    df, schema = source
    df.loc[0, column] = value
    with pytest.raises(ValueError, match=match):
        quality.validate_accidents(df, 2024, schema, {"TIPO_ACCIDENTE": {4}})


def test_duplicate_id_and_schema_drift(source):
    df, schema = source
    df.loc[1, "ID_ACCIDENTE"] = 1
    with pytest.raises(ValueError, match="duplicate"):
        quality.validate_accidents(df, 2024, schema, {})
    with pytest.raises(ValueError, match="schema"):
        quality.validate_accidents(df.drop(columns="HORA"), 2024, schema, {})
