from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.policy.tiers import compute_approval_tiers
from src.policy.triggers import (
    check_legal_triggers,
    check_privacy_triggers,
    check_security_triggers,
)


class PolicyBoundaryTests(unittest.TestCase):
    def test_tier_boundaries(self):
        self.assertEqual(compute_approval_tiers(1000.00), ["Manager"])
        self.assertEqual(
            compute_approval_tiers(1000.01),
            ["Department Head", "Procurement"],
        )
        self.assertEqual(
            compute_approval_tiers(10000.00),
            ["Department Head", "Procurement"],
        )
        self.assertEqual(
            compute_approval_tiers(10000.01),
            ["Department Head", "Finance", "Procurement"],
        )
        self.assertEqual(
            compute_approval_tiers(25000.00),
            ["Department Head", "Finance", "Procurement"],
        )
        self.assertEqual(
            compute_approval_tiers(25000.01),
            ["Department Head", "Finance", "CFO", "Procurement"],
        )

    def test_security_triggers(self):
        self.assertTrue(
            check_security_triggers("source_code", [], {"is_registered": True, "api_status": "ok"}),
        )
        self.assertTrue(
            check_security_triggers(
                "internal_docs",
                ["Production AWS cloud account"],
                {"is_registered": True, "api_status": "ok"},
            ),
        )
        self.assertTrue(
            check_security_triggers("none", [], {"is_expired": True, "is_registered": True}),
        )
        self.assertTrue(
            check_security_triggers("none", [], {"has_conflict": True, "is_registered": True}),
        )
        self.assertTrue(
            check_security_triggers("none", [], {"api_status": "unavailable", "is_registered": True}),
        )

    def test_privacy_triggers(self):
        self.assertTrue(check_privacy_triggers("customer_pii"))
        self.assertTrue(check_privacy_triggers("employee_pii"))
        self.assertFalse(check_privacy_triggers("internal_marketing"))

    def test_legal_triggers(self):
        self.assertTrue(
            check_legal_triggers({"is_registered": False, "registry_status": "new_vendor"}, 10000.00),
        )
        self.assertTrue(
            check_legal_triggers({"is_registered": True, "registry_status": "new"}, 15000.00),
        )
        self.assertFalse(
            check_legal_triggers({"is_registered": True, "registry_status": "approved", "legal_terms_status": "approved"}, 5000.00),
        )


if __name__ == "__main__":
    unittest.main()
