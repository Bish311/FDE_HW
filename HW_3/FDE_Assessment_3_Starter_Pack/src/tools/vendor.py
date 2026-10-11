from __future__ import annotations

from datetime import date

from src.data_access import load_vendors
from src.tools.ledger import EvidenceLedger
from src.vendor_client import get_vendor_risk

REFERENCE_DATE = date(2026, 9, 30)
MAX_ASSESSMENT_DAYS = 365


class VendorLookupTool:
    def __init__(self) -> None:
        self._vendors: list[dict[str, object]] = load_vendors()

    def lookup(
        self,
        vendor_name: str,
        ledger: EvidenceLedger | None = None,
    ) -> dict[str, object]:
        internal_record = self._find_vendor(vendor_name)
        api_response = get_vendor_risk(vendor_name)

        is_registered = internal_record is not None
        reg_status = str(internal_record.get("procurement_status")) if internal_record else "new_vendor"
        legal_terms = str(internal_record.get("legal_terms_status")) if internal_record else "unknown"
        reg_date_str = str(internal_record.get("security_review_date")) if internal_record else None

        is_expired = False
        days_old = None
        if reg_date_str is not None and reg_date_str != "None":
            try:
                review_dt = date.fromisoformat(reg_date_str)
                delta = (REFERENCE_DATE - review_dt).days
                days_old = delta
                if delta > MAX_ASSESSMENT_DAYS:
                    is_expired = True
            except ValueError:
                is_expired = True

        api_status = api_response.status
        api_data = api_response.data
        api_review_status = None
        if api_data is not None:
            api_review_status = str(api_data.get("security_review_status"))

        has_conflict = False
        if is_registered and api_review_status is not None:
            reg_norm = reg_status.strip().lower()
            api_norm = api_review_status.strip().lower()
            if reg_norm == "approved" and api_norm in ["expired", "not_completed"]:
                has_conflict = True

        self._record_evidence(
            vendor_name,
            is_registered,
            reg_status,
            api_status,
            api_review_status,
            is_expired,
            has_conflict,
            ledger,
        )

        return {
            "vendor_name": vendor_name,
            "is_registered": is_registered,
            "registry_status": reg_status,
            "legal_terms_status": legal_terms,
            "api_status": api_status,
            "api_review_status": api_review_status,
            "is_expired": is_expired,
            "days_since_review": days_old,
            "has_conflict": has_conflict,
        }

    def _record_evidence(
        self,
        name: str,
        reg: bool,
        r_status: str,
        a_status: str,
        a_review: str | None,
        exp: bool,
        conflict: bool,
        ledger: EvidenceLedger | None,
    ) -> None:
        if ledger is None:
            return
        finding_reg = f"Vendor '{name}' registry status: {r_status} (Registered: {reg})"
        if exp:
            finding_reg = f"{finding_reg} - EXPIRED (>365 days from reference date 2026-09-30)"
        ledger.record("vendor_registry", finding_reg, f"vendors.csv:{name}")

        finding_api = f"Vendor-risk service for '{name}': call {a_status}, assessment: {a_review}"
        ledger.record("vendor_risk_service", finding_api, f"/vendor-risk/{name}")

        if conflict:
            c_msg = f"CONFLICT: Registry states '{r_status}' but vendor-risk service states '{a_review}'"
            ledger.record("vendor_reconciliation", c_msg, "vendors.csv vs /vendor-risk")

    def _find_vendor(self, vendor_name: str) -> dict[str, object] | None:
        target = vendor_name.strip().lower()
        for v in self._vendors:
            name = str(v.get("vendor_name") or "").strip().lower()
            if name == target:
                return v
        return None
