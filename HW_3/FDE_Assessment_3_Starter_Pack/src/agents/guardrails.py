from __future__ import annotations

from src.contracts import EvidenceItem, ProcurementDecision, RunTelemetry
from src.policy.engine import PolicyReceipt


class DecisionGuardrail:
    def enforce(
        self,
        request_id: str,
        recommendation: str,
        next_step: str,
        proposed_approvals: list[str],
        proposed_flags: list[str],
        proposed_missing: list[str],
        policy_receipt: PolicyReceipt,
        evidence_items: list[EvidenceItem],
        telemetry: RunTelemetry | None = None,
    ) -> ProcurementDecision:
        final_approvals: list[str] = list(policy_receipt.required_approvals)
        for app in proposed_approvals:
            if app not in final_approvals:
                final_approvals.append(app)

        final_flags: list[str] = list(policy_receipt.risk_flags)
        for flg in proposed_flags:
            if flg not in final_flags:
                final_flags.append(flg)

        final_missing: list[str] = list(policy_receipt.missing_information)
        for mis in proposed_missing:
            if mis not in final_missing:
                final_missing.append(mis)

        cleaned_rec = self._sanitize_text(recommendation)
        cleaned_step = self._sanitize_text(next_step)

        return ProcurementDecision(
            request_id=request_id,
            recommendation=cleaned_rec,
            evidence=evidence_items,
            required_approvals=final_approvals,
            missing_information=final_missing,
            risk_flags=final_flags,
            next_step=cleaned_step,
            human_review_required=True,
            telemetry=telemetry,
        )

    def _sanitize_text(self, text: str) -> str:
        prohibited = ["i have approved", "purchase completed", "spend authorized", "contract signed"]
        lowered = text.lower()
        for phrase in prohibited:
            if phrase in lowered:
                return "Recommend routing for formal policy and human review."
        return text
