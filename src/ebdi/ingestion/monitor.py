"""Read-only source checks; changed originals are quarantined, never activated."""

import hashlib
import io
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import urlopen

import pandas as pd
import pdfplumber
import requests

from ebdi.ingestion.download import catalog
from ebdi.utils.io import write_json


def validate_candidate(source: dict, payload: bytes) -> str:
    if source["format"] == "xlsx":
        if not payload.startswith(b"PK"):
            raise ValueError("Expected XLSX archive")
        sheets = pd.ExcelFile(io.BytesIO(payload), engine="calamine").sheet_names
        required = (
            "V_4"
            if source["id"].startswith("dgt_vehicles")
            else "P_6_1_1_10"
            if source["id"].startswith("dgt_drivers")
            else None
        )
        if required and required not in sheets:
            raise ValueError(f"Missing worksheet {required}")
        return f"Readable XLSX; {len(sheets)} sheets; semantic audit still required"
    if source["format"] == "pdf":
        if not payload.startswith(b"%PDF-"):
            raise ValueError("Expected PDF signature")
        with pdfplumber.open(io.BytesIO(payload)) as pdf:
            if not pdf.pages:
                raise ValueError("Empty PDF")
            return f"Readable PDF; {len(pdf.pages)} pages; table contracts require audit"
    if source["format"] == "json":
        value = json.loads(payload)
        if source["id"].startswith("eurostat") and not {"dimension", "value", "id", "size"} <= set(
            value
        ):
            raise ValueError("Missing JSON-stat contract fields")
        return "Readable JSON; grain/values require semantic audit"
    if b"<html" in payload[:500].lower() or not payload.strip():
        raise ValueError("Unexpected HTML or empty source")
    return "Nonempty payload; source-specific semantic audit required"


def probe_source(root: Path, source: dict) -> dict:
    record = {"id": source["id"], "audited_sha256": source["sample_sha256"]}
    try:
        if source.get("transport") == "urllib":
            with urlopen(source["url"], timeout=45) as response:
                payload = response.read()
        else:
            response = requests.get(source["url"], timeout=(10, 45))
            response.raise_for_status()
            payload = response.content
        digest = hashlib.sha256(payload).hexdigest()
        record["retrieved_sha256"] = digest
        if digest == source["sample_sha256"]:
            record["status"] = "unchanged"
        else:
            destination = root / "data/raw/quarantine" / digest / source["filename"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                destination.write_bytes(payload)
            record["status"] = "needs_review"
            record["quarantine_path"] = destination.relative_to(root).as_posix()
            try:
                record["structural_check"] = validate_candidate(source, payload)
            except (ValueError, KeyError, OSError) as error:
                record["status"] = "invalid_revision"
                record["structural_check"] = str(error)
    except Exception as error:
        record["status"] = "unavailable"
        record["error"] = f"{type(error).__name__}: {str(error)[:300]}"
    return record


def monitor_sources(root: Path) -> dict:
    sources = [source for source in catalog(root) if source["enabled"]]
    with ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(lambda source: probe_source(root, source), sources))
    report = {
        "checked_at": datetime.now(UTC).isoformat(),
        "active_sources_changed": False,
        "sources": records,
        "attention_required": any(r["status"] != "unchanged" for r in records),
    }
    write_json(root / "outputs/tables/source_monitor.json", report)
    return report
