from ebdi.ingestion.europe import decode_jsonstat


def test_sparse_observations_preserve_flags_and_never_become_zero():
    data = {
        "class": "dataset",
        "id": ["geo", "time"],
        "size": [2, 2],
        "dimension": {
            "geo": {"category": {"index": {"ES": 0, "PT": 1}}},
            "time": {"category": {"index": {"2023": 0, "2024": 1}}},
        },
        "value": {"0": 10, "3": 0},
        "status": {"0": "p"},
    }
    df = decode_jsonstat(data)
    assert len(df) == 2
    assert df.iloc[0].to_dict() == {"geo": "ES", "time": "2023", "value": 10.0, "status": "p"}
    assert df.iloc[1]["value"] == 0
