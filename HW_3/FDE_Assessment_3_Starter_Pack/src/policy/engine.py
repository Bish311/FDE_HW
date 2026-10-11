from __future__ import annotations

from pydantic import BaseModel, Field

from src.policy.injection import detect_prompt_injection
from src.policy.tiers import compute_approval_tiers
from src.policy.triggers import (
    check_legal_triggers,
    check_privacy_triggers,
    check_security_triggers,
)


class PolicyReceipt(BaseModel):
    required_approvals: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_route: str
    is_fully_compliant: bool = False


class PolicyEngine:
    def evaluate(
        self,
        request_data: dict[str, object],
        budget_data: dict[str, object],
        vendor_data: dict[str, object],
        catalog_data: dict[str, object],
    ) -> PolicyReceipt:
        approvals: list[str] = []
        flags: list[str] = []
        missing: list[str] = []

        cost_raw = request_data.get("annual_cost_usd")
        annual_cost: float | None = float(cost_raw) if cost_raw is not None else None

        missing = self._check_missing_fields(request_data)
        if len(missing) > 0:
            flags.append("missing_information")

        base_tiers = compute_approval_tiers(annual_cost)
        for t in base_tiers:
            if t not in approvals:
                approvals.append(t)

        if budget_data.get("is_sufficient") is False:
            flags.append("budget_insufficient")
            if "Finance" not in approvals:
                approvals.append("Finance")

        if catalog_data.get("has_overlap") is True:
            flags.append("existing_tool_overlap")

        integrations_raw = request_data.get("requested_integrations") or []
        integrations: list[str] = []
        for item in integrations_raw:
            integrations.append(str(item))

        data_access = str(request_data.get("data_access_level") or "")

        if check_security_triggers(data_access, integrations, vendor_data):
            flags.append("security_review_required")
            if "Security" not in approvals:
                approvals.append("Security")

        if vendor_data.get("is_expired") is True:
            flags.append("vendor_review_expired")

        if vendor_data.get("has_conflict") is True:
            flags.append("conflicting_vendor_evidence")

        if vendor_data.get("api_status") == "unavailable":
            flags.append("vendor_risk_unavailable")

        if check_privacy_triggers(data_access):
            flags.append("privacy_review_required")
            if "Privacy" not in approvals:
                approvals.append("Privacy")

        if check_legal_triggers(vendor_data, annual_cost):
            flags.append("legal_review_required")
            if "Legal" not in approvals:
                approvals.append("Legal")

        texts_to_scan = [
            str(request_data.get("business_justification") or ""),
            str(request_data.get("product_name") or ""),
        ]
        if detect_prompt_injection(texts_to_scan):
            flags.append("prompt_injection_detected")

        route = self._determine_route(flags)
        is_compliant = len(flags) == 0 and len(missing) == 0

        return PolicyReceipt(
            required_approvals=approvals,
            risk_flags=flags,
            missing_information=missing,
            recommended_route=route,
            is_fully_compliant=is_compliant,
        )

    def _check_missing_fields(self, req: dict[str, object]) -> list[str]:
        missing: list[str] = []
        if req.get("annual_cost_usd") is None:
            missing.append("annual cost")
        if req.get("user_count") is None:
            missing.append("user count")
        data_lvl = str(req.get("data_access_level") or "").strip().lower()
        if not data_lvl or data_lvl == "unknown":
            missing.append("data access level")
        if not req.get("business_justification"):
            missing.append("business justification")
        if not req.get("product_name"):
            missing.append("product name")
        if not req.get("vendor_name"):
            missing.append("vendor name")
        return missing

    def _determine_route(self, flags: list[str]) -> str:
        if "missing_information" in flags:
            return "request_clarification"
        if "prompt_injection_detected" in flags:
            return "escalate_security_review"
        if "vendor_risk_unavailable" in flags or "conflicting_vendor_evidence" in flags:
            return "escalate_manual_review"
        if "budget_insufficient" in flags:
            return "finance_budget_exception"
        if "security_review_required" in flags or "privacy_review_required" in flags or "legal_review_required" in flags:
            return "specialist_review"
        if "existing_tool_overlap" in flags:
            return "evaluate_existing_alternatives"
        return "route_for_approval"
