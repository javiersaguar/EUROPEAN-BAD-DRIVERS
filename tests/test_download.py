import hashlib
from pathlib import Path

import pytest
import requests
import yaml

from ebdi.ingestion.download import download, raw_path


def setup_source(root: Path, expected: bytes):
    (root / "configs").mkdir()
    source = {
        "id": "sample",
        "url": "https://publisher.example/data.csv",
        "format": "csv",
        "filename": "sample.csv",
        "enabled": True,
        "sample_sha256": hashlib.sha256(expected).hexdigest(),
    }
    (root / "configs/sources.yaml").write_text(yaml.safe_dump({"sources": [source]}))


def response(payload: bytes, status: int = 200):
    reply = requests.Response()
    reply.status_code = status
    reply._content = payload
    reply.headers["Content-Type"] = "text/csv"
    return reply


def test_immutable_revisions_and_cache_integrity(tmp_path, monkeypatch):
    original, revised = b"count\n1\n", b"count\n2\n"
    setup_source(tmp_path, original)
    monkeypatch.setattr(requests.Session, "get", lambda *args, **kwargs: response(original))
    download(tmp_path)
    old_path = raw_path(tmp_path, "sample")
    assert "revisions" in old_path.parts
    monkeypatch.setattr(requests.Session, "get", lambda *args, **kwargs: response(revised))
    download(tmp_path)  # Must use the verified cache, not silently accept the revision.
    assert raw_path(tmp_path, "sample") == old_path
    download(tmp_path, refresh=True)
    assert old_path.read_bytes() == original
    current = raw_path(tmp_path, "sample")
    assert current != old_path and current.read_bytes() == revised
    current.write_bytes(b"modified")
    with pytest.raises(ValueError, match="modified"):
        raw_path(tmp_path, "sample")


def test_changed_publisher_hash_requires_audit_and_http_errors_are_not_cached(
    tmp_path, monkeypatch
):
    setup_source(tmp_path, b"expected")
    monkeypatch.setattr(requests.Session, "get", lambda *args, **kwargs: response(b"new revision"))
    with pytest.raises(ValueError, match="revision"):
        download(tmp_path)
    assert not (tmp_path / "data/raw/manifest.json").exists()
    monkeypatch.setattr(
        requests.Session, "get", lambda *args, **kwargs: response(b"forbidden", 403)
    )
    with pytest.raises(requests.HTTPError):
        download(tmp_path)
    assert not (tmp_path / "data/raw/manifest.json").exists()


def test_html_is_not_an_excel_workbook(tmp_path, monkeypatch):
    setup_source(tmp_path, b"html")
    path = tmp_path / "configs/sources.yaml"
    source = yaml.safe_load(path.read_text())
    source["sources"][0]["format"] = "xlsx"
    path.write_text(yaml.safe_dump(source))
    monkeypatch.setattr(requests.Session, "get", lambda *args, **kwargs: response(b"html"))
    with pytest.raises(ValueError, match="XLSX"):
        download(tmp_path)


def test_manifest_not_present_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError, match="download"):
        raw_path(tmp_path, "sample")
