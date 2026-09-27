import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Any
import urllib.request
import urllib.error

logger = logging.getLogger("pipeline.ingest_api")

def _fetch_from_disk_cache(cache_dir: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    page_files: List[Path] = sorted(cache_dir.glob("page_*.json"))
    for file_path in page_files:
        content_text: str = file_path.read_text(encoding="utf-8")
        payload: Dict[str, Any] = json.loads(content_text)
        page_items: List[Dict[str, Any]] = payload.get("data", [])
        for item in page_items:
            records.append(item)
    logger.info("Loaded %d dispatch records from disk cache %s", len(records), cache_dir)
    return records

def fetch_dispatch_orders(
    endpoint_url: str,
    cache_dir: Path,
    max_pages: int,
    page_size: int,
    expected_total: int,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    api_available: bool = True
    for page_num in range(1, max_pages + 1):
        url: str = f"{endpoint_url}?page={page_num}&page_size={page_size}"
        request = urllib.request.Request(url, headers={"User-Agent": "FlashEats-FDE/1.0"})
        success: bool = False
        attempts: int = 0
        while not success and attempts < 3 and api_available:
            attempts = attempts + 1
            try:
                with urllib.request.urlopen(request, timeout=1.0) as response:
                    raw_data: bytes = response.read()
                    data_obj: Dict[str, Any] = json.loads(raw_data.decode("utf-8"))
                    page_items: List[Dict[str, Any]] = data_obj.get("data", [])
                    for item in page_items:
                        records.append(item)
                    success = True
            except urllib.error.HTTPError as http_err:
                if http_err.code == 429:
                    retry_header: str = http_err.headers.get("retry_after_seconds", "1")
                    time.sleep(float(retry_header))
                elif http_err.code == 500:
                    time.sleep(0.1 * attempts)
                else:
                    api_available = False
            except (urllib.error.URLError, TimeoutError, ConnectionRefusedError, OSError):
                api_available = False
        if not api_available:
            break
    if len(records) == expected_total:
        logger.info("Successfully fetched %d records from live REST API", len(records))
        return records
    logger.warning("Live API unavailable or incomplete. Falling back to audited raw disk cache.")
    return _fetch_from_disk_cache(cache_dir)
