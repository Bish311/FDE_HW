from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "vendor_risk.json").read_text(encoding="utf-8"))

app = FastAPI(title="Vendor Risk Service", version="1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/vendor-risk/{vendor_name}")
def vendor_risk(vendor_name: str) -> dict[str, object]:
    record = DATA.get(vendor_name)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No vendor-risk record for '{vendor_name}'",
        )
    if record.get("force_error"):
        error_msg = str(record.get("error_message", "Vendor-risk service unavailable"))
        raise HTTPException(status_code=503, detail=error_msg)
    response_payload: dict[str, object] = {"vendor_name": vendor_name}
    for key, value in record.items():
        response_payload[key] = value
    return response_payload
