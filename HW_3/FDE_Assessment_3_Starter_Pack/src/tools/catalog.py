from __future__ import annotations

from src.data_access import load_purchase_history, load_software_catalog
from src.tools.ledger import EvidenceLedger


class CatalogSearchTool:
    def __init__(self) -> None:
        self._catalog: list[dict[str, object]] = load_software_catalog()
        self._history: list[dict[str, object]] = load_purchase_history()

    def search_overlap(
        self,
        product_name: str,
        category: str,
        vendor_name: str,
        ledger: EvidenceLedger | None = None,
    ) -> dict[str, object]:
        matched_catalog: list[dict[str, object]] = []
        target_prod = product_name.strip().lower()
        target_cat = category.strip().lower()
        target_ven = vendor_name.strip().lower()

        for item in self._catalog:
            p_name = str(item.get("product_name") or "").strip().lower()
            c_name = str(item.get("category") or "").strip().lower()
            v_name = str(item.get("vendor_name") or "").strip().lower()

            is_match = False
            if target_prod in p_name or p_name in target_prod:
                is_match = True
            if target_cat == c_name:
                is_match = True
            if target_ven == v_name:
                is_match = True

            if is_match:
                matched_catalog.append(item)

        has_overlap = len(matched_catalog) > 0
        if has_overlap:
            names: list[str] = []
            for m in matched_catalog:
                names.append(str(m.get("product_name")))
            names_str = ", ".join(names)
            finding = f"Existing software overlap found in category '{category}': {names_str}"
        else:
            finding = f"No existing software overlap identified for '{product_name}' in category '{category}'"

        if ledger is not None:
            ledger.record("software_catalog", finding, "software_catalog.csv")

        return {
            "has_overlap": has_overlap,
            "matched_tools": matched_catalog,
        }
