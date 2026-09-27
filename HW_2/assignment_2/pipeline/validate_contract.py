import logging
from typing import List, Dict, Set, Tuple
from pipeline.models import OrderRecord, QuarantineItem

logger = logging.getLogger("pipeline.validate_contract")

def run_contract_audit(
    raw_orders: List[OrderRecord],
) -> Tuple[List[OrderRecord], List[QuarantineItem], Dict[str, int]]:
    seen_ids: Set[str] = set()
    clean_orders: List[OrderRecord] = []
    quarantine: List[QuarantineItem] = []
    stats: Dict[str, int] = {
        "raw_count": len(raw_orders),
        "duplicates": 0,
        "inverted_prometa": 0,
        "pickup_after_delivery": 0,
        "null_delivered": 0,
    }

    for order in raw_orders:
        order_id: str = order["order_id"]
        if order_id in seen_ids:
            stats["duplicates"] = stats["duplicates"] + 1
            item: QuarantineItem = {
                "order_id": order_id,
                "reason": "duplicate_primary_key",
                "severity": "WARN",
                "record_payload": dict(order),
            }
            quarantine.append(item)
            continue

        seen_ids.add(order_id)
        clean_orders.append(order)

        created_at: str = order["created_at"]
        promised_eta: str = order["promised_eta"]
        pickup_at = order["pickup_at"]
        actual_delivery_at = order["actual_delivery_at"]
        final_status: str = order["final_status"].lower()

        if promised_eta < created_at:
            stats["inverted_prometa"] = stats["inverted_prometa"] + 1
            item_inv: QuarantineItem = {
                "order_id": order_id,
                "reason": "promised_eta_prior_to_created_at",
                "severity": "FAIL",
                "record_payload": dict(order),
            }
            quarantine.append(item_inv)

        if pickup_at and actual_delivery_at and pickup_at > actual_delivery_at:
            stats["pickup_after_delivery"] = stats["pickup_after_delivery"] + 1
            item_chron: QuarantineItem = {
                "order_id": order_id,
                "reason": "pickup_timestamp_after_actual_delivery",
                "severity": "FAIL",
                "record_payload": dict(order),
            }
            quarantine.append(item_chron)

        if final_status == "delivered" and (not actual_delivery_at or actual_delivery_at == ""):
            stats["null_delivered"] = stats["null_delivered"] + 1

    logger.info("Contract audit completed. Clean orders: %d, Quarantined events: %d", len(clean_orders), len(quarantine))
    return clean_orders, quarantine, stats
