from __future__ import annotations

from src.data_access import load_budgets
from src.tools.ledger import EvidenceLedger


class BudgetCheckTool:
    def __init__(self) -> None:
        self._budgets: list[dict[str, object]] = load_budgets()

    def check_budget(
        self,
        department: str,
        annual_cost_usd: float | None,
        ledger: EvidenceLedger | None = None,
    ) -> dict[str, object]:
        dept_budget = self._find_department(department)
        if dept_budget is None:
            finding = f"Department '{department}' not found in budget registry"
            if ledger is not None:
                ledger.record("budget_check", finding, "department_budgets.csv")
            return {
                "found": False,
                "is_sufficient": False,
                "available_usd": 0,
                "cost_usd": annual_cost_usd or 0,
            }

        available = int(dept_budget.get("available_usd") or 0)
        cost = annual_cost_usd if annual_cost_usd is not None else 0.0
        is_sufficient = cost <= available

        finding = (
            f"Department {department} annual software budget available: "
            f"${available:,}. Requested cost: ${cost:,.2f}. "
            f"Budget check: {'Passed' if is_sufficient else 'INSUFFICIENT'}"
        )
        if ledger is not None:
            ledger.record("budget_check", finding, f"department_budgets.csv:{department}")

        return {
            "found": True,
            "department": department,
            "available_usd": available,
            "annual_cost_usd": cost,
            "is_sufficient": is_sufficient,
        }

    def _find_department(self, department: str) -> dict[str, object] | None:
        target = department.strip().lower()
        for b in self._budgets:
            name = str(b.get("department") or "").strip().lower()
            if name == target:
                return b
        return None
