from __future__ import annotations

import os
import time
from urllib.parse import quote

import requests
from pydantic import BaseModel, Field

DEFAULT_TIMEOUT_SECONDS = 3.0
MAX_ATTEMPTS = 2
BACKOFF_SECONDS = 0.2


class VendorRiskResponse(BaseModel):
    status: str = Field(description="ok, not_found, or unavailable")
    vendor_name: str
    data: dict[str, object] | None = None
    error_message: str | None = None


def get_vendor_risk(
    vendor_name: str,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> VendorRiskResponse:
    base_url = os.getenv("VENDOR_RISK_BASE_URL", "http://127.0.0.1:8001").rstrip("/")
    target_url = f"{base_url}/vendor-risk/{quote(vendor_name, safe='')}"

    for attempt in range(MAX_ATTEMPTS):
        try:
            resp = requests.get(target_url, timeout=timeout_seconds)
            if resp.status_code == 200:
                payload = resp.json()
                return VendorRiskResponse(
                    status="ok",
                    vendor_name=vendor_name,
                    data=payload,
                )
            if resp.status_code == 404:
                return VendorRiskResponse(
                    status="not_found",
                    vendor_name=vendor_name,
                    error_message=f"No record for vendor {vendor_name}",
                )
            if resp.status_code == 503:
                return VendorRiskResponse(
                    status="unavailable",
                    vendor_name=vendor_name,
                    error_message="Vendor risk service returned 503",
                )
        except (requests.ConnectionError, requests.Timeout) as err:
            if attempt == MAX_ATTEMPTS - 1:
                return VendorRiskResponse(
                    status="unavailable",
                    vendor_name=vendor_name,
                    error_message=str(err),
                )
            time.sleep(BACKOFF_SECONDS)
    return VendorRiskResponse(
        status="unavailable",
        vendor_name=vendor_name,
        error_message="Service unreachable after retries",
    )
