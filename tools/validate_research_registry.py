from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
FILES = (
    "studies.json",
    "datasets.json",
    "releases.json",
    "replications.json",
    "reviews.json",
    "applications.json",
    "publications.json",
    "deviations.json",
    "benchmarks.json",
)
REQUIRED = {"id", "title", "status", "updated"}


def load_records(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path}: root must be a JSON array")
    records: list[dict[str, Any]] = []
    for index, value in enumerate(data):
        if not isinstance(value, dict):
            raise ValueError(f"{path}[{index}]: record must be an object")
        missing = REQUIRED - value.keys()
        if missing:
            raise ValueError(f"{path}[{index}]: missing {sorted(missing)}")
        records.append(value)
    return records


def validate() -> None:
    seen: dict[str, Path] = {}
    for name in FILES:
        path = REGISTRY / name
        if not path.exists():
            raise ValueError(f"missing registry file: {path}")
        for record in load_records(path):
            record_id = str(record["id"])
            if record_id in seen:
                raise ValueError(f"duplicate id {record_id!r}: {seen[record_id]} and {path}")
            seen[record_id] = path
    print(f"validated {len(FILES)} registry files and {len(seen)} records")


if __name__ == "__main__":
    validate()
