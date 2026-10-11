from __future__ import annotations

from src.agents.single import SingleProcurementAgent
from src.agents.staged import StagedProcurementSystem
from src.contracts import Architecture, ProcurementDecision
from src.mock_starter import ensure_mock_api_running

_SINGLE_AGENT: SingleProcurementAgent | None = None
_STAGED_AGENT: StagedProcurementSystem | None = None


def handle_request(request_id: str, architecture: Architecture = "single") -> ProcurementDecision:
    global _SINGLE_AGENT, _STAGED_AGENT
    ensure_mock_api_running()

    if architecture == "staged":
        if _STAGED_AGENT is None:
            _STAGED_AGENT = StagedProcurementSystem()
        return _STAGED_AGENT.run(request_id)

    if _SINGLE_AGENT is None:
        _SINGLE_AGENT = SingleProcurementAgent()
    return _SINGLE_AGENT.run(request_id)
