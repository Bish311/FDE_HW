import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger("pipeline.ingest_files")

def read_csv_records(file_path: Path) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    with open(file_path, mode="r", encoding="utf-8") as file_handle:
        reader = csv.DictReader(file_handle)
        for row in reader:
            records.append(dict(row))
    logger.info("Read %d records from %s", len(records), file_path.name)
    return records

def read_driver_events(file_path: Path) -> List[Dict[str, Any]]:
    with open(file_path, mode="r", encoding="utf-8") as file_handle:
        raw_events: List[Dict[str, Any]] = json.load(file_handle)
    total_events: int = 0
    for driver_entry in raw_events:
        event_list: List[Dict[str, Any]] = driver_entry.get("events", [])
        total_events = total_events + len(event_list)
    logger.info("Loaded %d couriers with %d total events from %s", len(raw_events), total_events, file_path.name)
    return raw_events
