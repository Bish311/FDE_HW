from __future__ import annotations

from src.agents.guardrails import DecisionGuardrail
from src.contracts import ProcurementDecision, RunTelemetry
from src.data_access import get_request
from src.llm.decider import evaluate_request_decisions
from src.llm.synthesizer import synthesize_recommendation_and_next_step
from src.policy.engine import PolicyEngine, PolicyReceipt
from src.tools.budget import BudgetCheckTool
from src.tools.catalog import CatalogSearchTool
from src.tools.ledger import EvidenceLedger
from src.tools.requester import RequesterProfileTool
from src.tools.vendor import VendorLookupTool


class ProcurementAnalystAgent:
    def __init__(self) -> None:
        self._requester_tool = RequesterProfileTool()
        self._budget_tool = BudgetCheckTool()
        self._catalog_tool = CatalogSearchTool()
        self._vendor_tool = VendorLookupTool()

    def gather_evidence(self, req: dict[str, object], ledger: EvidenceLedger) -> dict[str, object]:
        req_id = str(req.get("requester_id") or "")
        profile = self._requester_tool.get_profile(req_id, ledger)

        dept = str(req.get("department") or "")
        if not dept and profile.get("found"):
            emp_obj = profile.get("requester")
            if isinstance(emp_obj, dict):
                dept = str(emp_obj.get("department") or "")

        cost_raw = req.get("annual_cost_usd")
        cost: float | None = float(cost_raw) if cost_raw is not None else None
        budget = self._budget_tool.check_budget(dept, cost, ledger)

        prod = str(req.get("product_name") or "")
        cat = str(req.get("category") or "")
        ven = str(req.get("vendor_name") or "")
        catalog = self._catalog_tool.search_overlap(prod, cat, ven, ledger)

        vendor = self._vendor_tool.lookup(ven, ledger)

        return {
            "profile": profile,
            "budget": budget,
            "catalog": catalog,
            "vendor": vendor,
        }


class PolicyReviewerAgent:
    def review(
        self,
        req: dict[str, object],
        evidence_pack: dict[str, object],
        policy_receipt: PolicyReceipt,
        ledger: EvidenceLedger,
    ) -> dict[str, str]:
        catalog = evidence_pack.get("catalog", {})
        tools_list: list[str] = []
        if isinstance(catalog, dict) and catalog.get("has_overlap"):
            for item in catalog.get("matched_tools", []):
                tools_list.append(str(item.get("product_name")))

        prod = str(req.get("product_name") or "")
        just_text = str(req.get("business_justification") or "")
        decisions = evaluate_request_decisions(prod, just_text, tools_list)

        if len(tools_list) > 0:
            ov_res = decisions["overlap_decision"]
            conf = ov_res.get("confidence", 0.0)
            ledger.record("mercury_classifier", f"Overlap classification: {ov_res.get('decision')} (confidence {conf})")

        inj_res = decisions["is_injection"]
        conf_inj = inj_res.get("confidence", 0.0)
        ledger.record("mercury_classifier", f"Prompt injection classification: {inj_res.get('decision')} (confidence {conf_inj})")

        evidence_items = ledger.get_items()
        findings: list[str] = []
        for item in evidence_items:
            findings.append(f"{item.source}: {item.finding}")

        policy_dict: dict[str, object] = {
            "required_approvals": policy_receipt.required_approvals,
            "risk_flags": policy_receipt.risk_flags,
            "recommended_route": policy_receipt.recommended_route,
        }
        return synthesize_recommendation_and_next_step(req, policy_dict, findings)


class StagedProcurementSystem:
    def __init__(self) -> None:
        self._analyst = ProcurementAnalystAgent()
        self._reviewer = PolicyReviewerAgent()
        self._policy_engine = PolicyEngine()
        self._guardrail = DecisionGuardrail()

    def run(self, request_id: str) -> ProcurementDecision:
        ledger = EvidenceLedger()
        tool_names = ["requester_profile", "budget_check", "catalog_search", "vendor_lookup"]
        req = get_request(request_id)

        evidence_pack = self._analyst.gather_evidence(req, ledger)
        budget = evidence_pack["budget"]
        vendor = evidence_pack["vendor"]
        catalog = evidence_pack["catalog"]

        receipt = self._policy_engine.evaluate(req, budget, vendor, catalog)
        copy = self._reviewer.review(req, evidence_pack, receipt, ledger)

        telemetry = RunTelemetry(
            llm_calls=2,
            tool_calls=4,
            tool_names=tool_names,
        )

        return self._guardrail.enforce(
            request_id=request_id,
            recommendation=copy["recommendation"],
            next_step=copy["next_step"],
            proposed_approvals=[],
            proposed_flags=[],
            proposed_missing=[],
            policy_receipt=receipt,
            evidence_items=ledger.get_items(),
            telemetry=telemetry,
        )
