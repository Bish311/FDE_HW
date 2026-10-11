from __future__ import annotations

import csv
import json
from pathlib import Path

from src.core.errors import DataLoadError

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REFERENCE_DATE = "2026-09-30"


def read_csv_clean(filename: str) -> list[dict[str, object]]:
    filepath = DATA_DIR / filename
    if not filepath.is_file():
        raise DataLoadError(f"Missing data file: {filename}")
    cleaned_rows: list[dict[str, object]] = []
    with filepath.open(encoding="utf-8", newline="") as file_handle:
        reader = csv.DictReader(file_handle)
        for raw_row in reader:
            clean_row: dict[str, object] = {}
            for key, val in raw_row.items():
                if val is None or val == "":
                    clean_row[key] = None
                else:
                    clean_row[key] = val
            cleaned_rows.append(clean_row)
    return cleaned_rows


def load_employees() -> list[dict[str, object]]:
    return read_csv_clean("employees.csv")


def load_budgets() -> list[dict[str, object]]:
    return read_csv_clean("department_budgets.csv")


def load_software_catalog() -> list[dict[str, object]]:
    return read_csv_clean("software_catalog.csv")


def load_vendors() -> list[dict[str, object]]:
    return read_csv_clean("vendors.csv")


def load_purchase_history() -> list[dict[str, object]]:
    return read_csv_clean("purchase_history.csv")


def load_requests() -> list[dict[str, object]]:
    filepath = DATA_DIR / "requests.json"
    if not filepath.is_file():
        raise DataLoadError("Missing requests.json")
    raw_content = filepath.read_text(encoding="utf-8")
    parsed: list[dict[str, object]] = json.loads(raw_content)
    return parsed


def get_request(request_id: str) -> dict[str, object]:
    all_requests = load_requests()
    for req in all_requests:
        if req.get("request_id") == request_id:
            return req
    syn_file = ROOT / "evals" / "synthetic_cases.json"
    if syn_file.is_file():
        content = syn_file.read_text(encoding="utf-8")
        syn_cases: list[dict[str, object]] = json.loads(content)
        for sc in syn_cases:
            case_req = sc.get("request")
            if isinstance(case_req, dict) and case_req.get("request_id") == request_id:
                return case_req
    raise DataLoadError(f"Unknown request_id: {request_id}")


def load_policy_text() -> str:
    filepath = DATA_DIR / "procurement_policy.md"
    if not filepath.is_file():
        raise DataLoadError("Missing procurement_policy.md")
    return filepath.read_text(encoding="utf-8")
