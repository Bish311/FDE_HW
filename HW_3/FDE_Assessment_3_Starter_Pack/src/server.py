from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.contracts import Architecture
from src.core.errors import DataLoadError, ProcurementError
from src.data_access import get_request, load_requests
from src.mock_starter import ensure_mock_api_running
from src.solution import handle_request

ROOT = Path(__file__).resolve().parents[1]
AUDIT_LOG_FILE = ROOT / "data" / "audit_log.json"

server_app = FastAPI(title="AI Procurement Request Copilot API", version="1.0")

server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluateRequest(BaseModel):
    request_id: str
    architecture: Architecture = "single"


class HumanAuditAction(BaseModel):
    request_id: str
    reviewer: str = "Bish"
    action: str = Field(description="accept, reject, return, or override")
    justification: str
    decision_summary: dict[str, object] = Field(default_factory=dict)


@server_app.get("/api/health")
def api_health() -> dict[str, str]:
    return {"status": "ok"}


@server_app.get("/api/requests")
def list_requests() -> list[dict[str, object]]:
    return load_requests()


@server_app.get("/api/requests/{request_id}")
def fetch_request(request_id: str) -> dict[str, object]:
    try:
        return get_request(request_id)
    except (KeyError, DataLoadError) as err:
        raise HTTPException(status_code=404, detail=str(err))


@server_app.post("/api/evaluate")
def run_evaluation(payload: EvaluateRequest) -> dict[str, object]:
    ensure_mock_api_running()
    try:
        decision = handle_request(payload.request_id, architecture=payload.architecture)
        return decision.model_dump()
    except (KeyError, DataLoadError, ProcurementError, ValueError) as err:
        raise HTTPException(status_code=500, detail=str(err))


@server_app.get("/api/audit")
def list_audit_logs() -> list[dict[str, object]]:
    if not AUDIT_LOG_FILE.is_file():
        return []
    try:
        content = AUDIT_LOG_FILE.read_text(encoding="utf-8")
        parsed: list[dict[str, object]] = json.loads(content)
        return parsed
    except json.JSONDecodeError:
        return []


@server_app.post("/api/audit")
def record_audit(action: HumanAuditAction) -> dict[str, object]:
    logs = list_audit_logs()
    entry: dict[str, object] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "request_id": action.request_id,
        "reviewer": action.reviewer,
        "action": action.action,
        "justification": action.justification,
        "decision_summary": action.decision_summary,
    }
    logs.append(entry)
    AUDIT_LOG_FILE.write_text(json.dumps(logs, indent=2), encoding="utf-8")
    return {"status": "recorded", "entry": entry}
