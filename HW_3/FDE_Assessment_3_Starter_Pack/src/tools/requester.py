from __future__ import annotations

from src.data_access import load_employees
from src.tools.ledger import EvidenceLedger


class RequesterProfileTool:
    def __init__(self) -> None:
        self._employees: list[dict[str, object]] = load_employees()

    def get_profile(
        self,
        requester_id: str,
        ledger: EvidenceLedger | None = None,
    ) -> dict[str, object]:
        employee = self._find_employee(requester_id)
        if employee is None:
            finding = f"Requester ID {requester_id} not found in employee directory"
            if ledger is not None:
                ledger.record("requester_directory", finding, "employees.csv")
            return {"found": False, "requester_id": requester_id}

        manager_id = employee.get("manager_id")
        manager = None
        if manager_id is not None:
            manager = self._find_employee(str(manager_id))

        dept_head = self._find_department_head(employee)

        result: dict[str, object] = {
            "found": True,
            "requester": employee,
            "manager": manager,
            "department_head": dept_head,
        }

        finding = (
            f"Requester {employee.get('name')} ({employee.get('department')}, "
            f"Level: {employee.get('level')}). Manager: "
            f"{manager.get('name') if manager else 'None'}. Department Head: "
            f"{dept_head.get('name') if dept_head else 'None'}"
        )
        if ledger is not None:
            ledger.record("requester_directory", finding, f"employees.csv:{requester_id}")
        return result

    def _find_employee(self, employee_id: str) -> dict[str, object] | None:
        for emp in self._employees:
            if emp.get("employee_id") == employee_id:
                return emp
        return None

    def _find_department_head(self, start_emp: dict[str, object]) -> dict[str, object] | None:
        current = start_emp
        for _ in range(10):
            level = str(current.get("level") or "")
            if "Director" in level or "VP" in level:
                return current
            mgr_id = current.get("manager_id")
            if mgr_id is None:
                return current
            parent = self._find_employee(str(mgr_id))
            if parent is None:
                return current
            current = parent
        return current
