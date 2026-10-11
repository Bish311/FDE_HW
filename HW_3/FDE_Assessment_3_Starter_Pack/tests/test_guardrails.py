from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agents.guardrails import DecisionGuardrail
from src.contracts import EvidenceItem
from src.policy.engine import PolicyReceipt


class GuardrailTests(unittest.TestCase):
    def test_guardrail_floor_retention(self):
        guard = DecisionGuardrail()
        receipt = PolicyReceipt(
            required_approvals=["Department Head", "Finance", "Procurement", "Security"],
            risk_flags=["budget_insufficient", "security_review_required"],
            missing_information=[],
            recommended_route="specialist_review",
        )
        evidence = [EvidenceItem(source="tool", finding="E1 finding", reference="E1")]

        decision = guard.enforce(
            request_id="REQ-TEST",
            recommendation="I have approved this purchase.",
            next_step="Completed immediately.",
            proposed_approvals=["Manager"],
            proposed_flags=[],
            proposed_missing=[],
            policy_receipt=receipt,
            evidence_items=evidence,
        )

        for app in ["Department Head", "Finance", "Procurement", "Security"]:
            self.assertIn(app, decision.required_approvals)
        for flg in ["budget_insufficient", "security_review_required"]:
            self.assertIn(flg, decision.risk_flags)

        self.assertTrue(decision.human_review_required)
        self.assertNotIn("I have approved", decision.recommendation)


if __name__ == "__main__":
    unittest.main()
