"""Cached, verified public downloads with immutable revision storage."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.request import urlopen

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ebdi.utils.io import read_yaml, write_json


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def catalog(root: Path) -> list[dict[str, Any]]:
    return read_yaml(root / "configs/sources.yaml")["sources"]


def raw_path(root: Path, source_id: str) -> Path:
    manifest_path = root / "data/raw/manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        matches = [r for r in manifest if r["id"] == source_id]
        if matches:
            record = matches[-1]
            path = root / "data/raw" / record.get("raw_path", record["filename"])
            if sha256(path) != record["sha256"]:
                raise ValueError(f"Raw cache modified: {source_id}. Restore from source.")
            return path
    raise FileNotFoundError(f"Missing verified source {source_id}. Run ebdi download first.")


def download(root: Path, refresh: bool = False) -> list[dict[str, Any]]:
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    old = (
        json.loads((raw / "manifest.json").read_text(encoding="utf-8"))
        if (raw / "manifest.json").exists()
        else []
    )
    records = {r["id"]: r for r in old}
    session = requests.Session()
    session.headers["User-Agent"] = "EBDI/0.1 reproducible-research"
    session.mount(
        "https://",
        HTTPAdapter(
            max_retries=Retry(
                total=3, backoff_factor=0.8, status_forcelist=[429, 500, 502, 503, 504]
            )
        ),
    )
    for source in catalog(root):
        if not source["enabled"]:
            continue
        sid = source["id"]
        if sid in records and not refresh:
            raw_path(root, sid)
            print(f"Cached: {sid}", flush=True)
            continue
        # UNESPA's public PDF accepts urllib's standard request but rejects the
        # custom research client with HTTP 403. No browser/session credentials.
        if source.get("transport") == "urllib":
            with urlopen(source["url"], timeout=120) as response_stream:
                payload = response_stream.read()
                http_status = response_stream.status
                content_type = response_stream.headers.get("Content-Type")
        else:
            response = session.get(source["url"], timeout=(15, 120))
            response.raise_for_status()
            payload = response.content
            http_status = response.status_code
            content_type = response.headers.get("Content-Type")
        if source["format"] == "pdf" and not payload.startswith(b"%PDF-"):
            raise ValueError(f"{sid}: expected PDF, received {content_type}")
        if source["format"] == "xlsx" and not payload.startswith(b"PK"):
            raise ValueError(f"{sid}: expected XLSX, received {content_type}")
        digest = hashlib.sha256(payload).hexdigest()
        if digest != source["sample_sha256"] and not refresh:
            raise ValueError(
                f"{sid}: publisher revision differs from audited hash. Audit new schema, then use --refresh to retain a separate revision."
            )
        path = raw / "revisions" / digest / source["filename"]
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(payload)
        records[sid] = {
            "id": sid,
            "filename": source["filename"],
            "url": source["url"],
            "raw_path": path.relative_to(raw).as_posix(),
            "sha256": digest,
            "bytes": len(payload),
            "retrieved_at": datetime.now(UTC).isoformat(),
            "http_status": http_status,
            "content_type": content_type,
        }
        # Persist each successful download, so interrupted runs resume without re-fetching.
        write_json(raw / "manifest.json", list(records.values()))
        print(f"Downloaded: {sid} ({len(payload):,} bytes)", flush=True)
    return list(records.values())
