import logging
from typing import List, Dict, Any
from pipeline.models import ValidationVerdict, OrderRecord

logger = logging.getLogger("pipeline.validate_gate")

def audit_restaurant_freshness(
    orders: List[OrderRecord],
    restaurant_status: List[Dict[str, str]],
) -> Dict[str, Any]:
    order_pickup_map: Dict[str, str] = {}
    for order in orders:
        if order["pickup_at"]:
            order_pickup_map[order["order_id"]] = order["pickup_at"]

    stale_updates_after_pickup: int = 0
    covered_orders: set = set()
    for status_row in restaurant_status:
        order_id: str = status_row["order_id"]
        covered_orders.add(order_id)
        updated_at: str = status_row["last_updated_at"]
        pickup_time: str = order_pickup_map.get(order_id, "")
        if pickup_time and updated_at > pickup_time:
            stale_updates_after_pickup = stale_updates_after_pickup + 1

    coverage_pct: float = (len(covered_orders) / float(len(orders))) * 100.0 if orders else 0.0
    return {
        "status_rows": len(restaurant_status),
        "unique_orders_covered": len(covered_orders),
        "coverage_percent": round(coverage_pct, 2),
        "stale_updates_after_pickup": stale_updates_after_pickup,
    }

def evaluate_validation_gate(
    contract_stats: Dict[str, int],
    freshness_stats: Dict[str, Any],
) -> ValidationVerdict:
    verdict: ValidationVerdict = {
        "business_grain": "WARN" if contract_stats.get("duplicates", 0) > 0 else "PASS",
        "timestamp_chronology": "FAIL" if (contract_stats.get("pickup_after_delivery", 0) > 0 or contract_stats.get("inverted_prometa", 0) > 0) else "PASS",
        "kpi_definition": "FAIL",
        "category_semantics": "WARN",
        "cross_source_mapping": "WARN" if freshness_stats.get("coverage_percent", 0.0) < 50.0 else "PASS",
        "freshness": "FAIL" if freshness_stats.get("stale_updates_after_pickup", 0) > 0 else "PASS",
        "publish_56_percent": "FAIL",
    }
    logger.info("Validation Gate Evaluated: Final Publish Verdict = %s", verdict["publish_56_percent"])
    return verdict
