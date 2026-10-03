"""HTTPS availability and published aggregate-contract monitor; no telemetry."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]


def check(url: str) -> dict:
    if not url.startswith("https://"):
        raise ValueError("Production monitor requires HTTPS")
    with urlopen(url.rstrip("/") + "/health.json", timeout=30) as response:
        health = json.load(response)
    if (
        health.get("status") != "ok"
        or health.get("schema_version") != 1
        or health.get("province_years") != 156
    ):
        raise ValueError("Published health contract failed")
    with urlopen(url.rstrip("/") + "/data/observatory.json", timeout=30) as response:
        data = json.load(response)
    if data["release"] != health["release"] or len(data["tables"]["spain_metrics"]) != 156:
        raise ValueError("Publication and health versions do not agree")
    return {
        "checked_at": datetime.now(UTC).isoformat(),
        "availability": "ok",
        "release": data["release"],
        "audit_date": data["audit_date"],
        "url": url,
        "note": "Availability/version consistency only; source freshness is checked separately",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    result = check(args.url)
    (ROOT / "outputs/tables/site_monitor.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result))
