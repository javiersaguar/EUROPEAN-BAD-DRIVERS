"""Small shared helpers; all filesystem paths are relative to a project root."""

import json
from pathlib import Path
from typing import Any

import yaml


def read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )


def project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parents[3]]:
        if (candidate / "configs/sources.yaml").exists():
            return candidate
    raise FileNotFoundError("Run from the repository root, or supply --root.")
