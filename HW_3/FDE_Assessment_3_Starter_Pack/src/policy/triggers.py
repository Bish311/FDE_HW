from __future__ import annotations

LEGAL_SPEND_THRESHOLD = 10000.00

SECURITY_DATA_KEYWORDS = [
    "source_code",
    "production_telemetry",
    "confidential_documents",
    "employee_pii",
    "customer_pii",
    "credentials",
    "secrets",
]

SECURITY_INTEGRATION_KEYWORDS = [
    "git",
    "production",
    "cloud account",
    "repository",
    "cloud",
]

PRIVACY_DATA_KEYWORDS = [
    "employee_pii",
    "customer_pii",
]


def check_security_triggers(
    data_access_level: str | None,
    integrations: list[str],
    vendor_info: dict[str, object],
) -> bool:
    data_lvl = str(data_access_level or "").lower()
    for kw in SECURITY_DATA_KEYWORDS:
        if kw in data_lvl:
            return True

    for integ in integrations:
        i_norm = integ.lower()
        for kw in SECURITY_INTEGRATION_KEYWORDS:
            if kw in i_norm:
                return True

    if vendor_info.get("is_expired") is True:
        return True

    if vendor_info.get("has_conflict") is True:
        return True

    api_rev = str(vendor_info.get("api_review_status") or "").lower()
    if api_rev in ["expired", "not_completed"]:
        return True

    if vendor_info.get("api_status") == "unavailable":
        return True

    return vendor_info.get("is_registered") is False


def check_privacy_triggers(data_access_level: str | None) -> bool:
    data_lvl = str(data_access_level or "").lower()
    for kw in PRIVACY_DATA_KEYWORDS:
        if kw in data_lvl:
            return True
    return False


def check_legal_triggers(
    vendor_info: dict[str, object],
    annual_cost_usd: float | None,
) -> bool:
    cost = annual_cost_usd or 0.0
    reg_stat = str(vendor_info.get("registry_status") or "").strip().lower()
    is_new = vendor_info.get("is_registered") is False or reg_stat in ["new", "new_vendor"]
    if is_new and cost >= LEGAL_SPEND_THRESHOLD:
        return True

    legal_terms = str(vendor_info.get("legal_terms_status") or "").strip().lower()
    if legal_terms and legal_terms not in ["approved", "standard"]:
        return True

    api_rev = str(vendor_info.get("api_review_status") or "").lower()
    return bool(api_rev == "not_completed" and cost >= LEGAL_SPEND_THRESHOLD)
