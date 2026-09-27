from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from pipeline.models import OrderRecord

logger = logging.getLogger("pipeline.transform_mart")

def _calculate_delay_minutes(promised_str: str, actual_str: Optional[str]) -> Optional[float]:
    if not actual_str or actual_str == "":
        return None
    prom_dt = datetime.fromisoformat(promised_str)
    act_dt = datetime.fromisoformat(actual_str)
    delta_seconds: float = (act_dt - prom_dt).total_seconds()
    return round(delta_seconds / 60.0, 2)

def build_order_mart(
    clean_orders: List[OrderRecord],
    app_actions: List[Dict[str, str]],
    interventions: List[Dict[str, str]],
    outcomes: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    support_orders: set = set()
    cancel_orders: set = set()
    for act in app_actions:
        oid: str = act["order_id"]
        action_type: str = act.get("action_type", "")
        if action_type == "SUPPORT_OPENED":
            support_orders.add(oid)
        elif action_type == "CANCEL_ATTEMPTED":
            cancel_orders.add(oid)

    interventions_by_order: Dict[str, List[str]] = {}
    for item in interventions:
        oid = item["order_id"]
        if oid not in interventions_by_order:
            interventions_by_order[oid] = []
        interventions_by_order[oid].append(item.get("intervention_type", ""))

    outcome_by_order: Dict[str, str] = {}
    for out in outcomes:
        outcome_by_order[out["order_id"]] = out.get("outcome_bucket", "unknown")

    mart_records: List[Dict[str, Any]] = []
    for order in clean_orders:
        oid = order["order_id"]
        final_status: str = order["final_status"].strip().lower()
        actual_time = order["actual_delivery_at"]
        delay_min: Optional[float] = _calculate_delay_minutes(order["promised_eta"], actual_time)
        is_deliv: int = 1 if final_status == "delivered" else 0
        is_late_0: int = 1 if (delay_min is not None and delay_min > 0.0) else 0
        is_late_10: int = 1 if (delay_min is not None and delay_min > 10.0) else 0
        is_severe_20: int = 1 if (delay_min is not None and delay_min > 20.0) else 0

        int_list: List[str] = interventions_by_order.get(oid, [])
        record: Dict[str, Any] = {
            "order_id": oid,
            "customer_id": order["customer_id"],
            "restaurant_id": order["restaurant_id"],
            "driver_id": order["driver_id"],
            "city": order["city"],
            "created_at": order["created_at"],
            "promised_eta": order["promised_eta"],
            "pickup_at": order["pickup_at"] or "",
            "actual_delivery_at": actual_time or "",
            "final_status_norm": final_status,
            "distance_km_estimate": order["distance_km_estimate"],
            "traffic_bucket": order["traffic_bucket"].strip().lower(),
            "weather_bucket": order["weather_bucket"].strip().lower(),
            "delay_min": delay_min if delay_min is not None else "",
            "is_delivered": is_deliv,
            "is_late_0m": is_late_0,
            "is_late_10m": is_late_10,
            "is_severe_20m": is_severe_20,
            "support_opened_flag": 1 if oid in support_orders else 0,
            "cancel_attempted_flag": 1 if oid in cancel_orders else 0,
            "intervention_count": len(int_list),
            "intervention_types": ";".join(int_list),
            "outcome_bucket": outcome_by_order.get(oid, "unknown"),
        }
        mart_records.append(record)

    logger.info("Transformed %d unified orders into decision mart", len(mart_records))
    return mart_records
