"""Compare the overlapping reference index with a simpler explicit alternative."""

from pathlib import Path

import pandas as pd

from ebdi.metrics.index import composite

ALTERNATIVE = {"injury_crashes_per_100k_population": 0.5, "fatalities_per_100k_population": 0.5}


def alternative_index(root: Path) -> pd.DataFrame:
    panel = pd.read_csv(root / "outputs/tables/spain_metrics.csv", dtype={"province_code": str})
    result = pd.concat(
        [composite(group, ALTERNATIVE, "percentile", 30) for _, group in panel.groupby("year")],
        ignore_index=True,
    )
    result["definition"] = (
        "50% injury-crash burden + 50% 30-day death burden; no urban/collision subset double weighting; deaths and crashes still related"
    )
    result.to_csv(root / "outputs/tables/index_alternative.csv", index=False)
    return result
