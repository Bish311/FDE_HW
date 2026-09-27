import logging
from typing import List, Dict, Any
from pipeline.models import ScorecardMetrics

logger = logging.getLogger("pipeline.metrics_calc")

def calculate_scorecard(mart_records: List[Dict[str, Any]]) -> ScorecardMetrics:
    total_orders: int = len(mart_records)
    observed_delivered: int = 0
    unrecorded_deliv: int = 0
    cancelled_count: int = 0
    late_0_count: int = 0
    late_10_count: int = 0
    late_20_count: int = 0
    support_opened_count: int = 0
    intervention_count: int = 0

    for row in mart_records:
        if row["final_status_norm"] == "delivered":
            if row["actual_delivery_at"] != "":
                observed_delivered = observed_delivered + 1
                if row["is_late_0m"] == 1:
                    late_0_count = late_0_count + 1
                if row["is_late_10m"] == 1:
                    late_10_count = late_10_count + 1
                if row["is_severe_20m"] == 1:
                    late_20_count = late_20_count + 1
            else:
                unrecorded_deliv = unrecorded_deliv + 1
        elif row["final_status_norm"] == "cancelled":
            cancelled_count = cancelled_count + 1

        if row["support_opened_flag"] == 1:
            support_opened_count = support_opened_count + 1
        if row["intervention_count"] > 0:
            intervention_count = intervention_count + 1

    denom_deliv: float = float(observed_delivered) if observed_delivered > 0 else 1.0
    denom_total: float = float(total_orders) if total_orders > 0 else 1.0

    scorecard: ScorecardMetrics = {
        "total_orders": total_orders,
        "delivered_orders_observed": observed_delivered,
        "unrecorded_deliveries": unrecorded_deliv,
        "cancelled_orders": cancelled_count,
        "leadership_late_rate_percent": round((late_0_count / denom_deliv) * 100.0, 2),
        "support_operational_late_rate_percent": round((late_10_count / denom_deliv) * 100.0, 2),
        "severe_delay_rate_percent": round((late_20_count / denom_deliv) * 100.0, 2),
        "customer_escalation_rate_percent": round((support_opened_count / denom_total) * 100.0, 2),
        "proactive_intervention_rate_percent": round((intervention_count / denom_total) * 100.0, 2),
        "order_cancellation_rate_percent": round((cancelled_count / denom_total) * 100.0, 2),
    }

    logger.info("Scorecard metrics calculated successfully")
    return scorecard

def calculate_stakeholder_comparison(mart_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    observed_delivered: int = 0
    total_orders: int = len(mart_records)
    late_count: int = 0
    late_10_count: int = 0

    for row in mart_records:
        if row["final_status_norm"] == "delivered" and row["actual_delivery_at"] != "":
            observed_delivered = observed_delivered + 1
            if row["is_late_0m"] == 1:
                late_count = late_count + 1
            if row["is_late_10m"] == 1:
                late_10_count = late_10_count + 1

    comparison: List[Dict[str, Any]] = [
        {"stakeholder": "VP Operations (Delivered)", "formula": "delay > 0m on observed delivered", "rate": round((late_count / float(observed_delivered)) * 100.0, 2)},
        {"stakeholder": "Support Lead (Actionable SLA)", "formula": "delay > 10m on observed delivered", "rate": round((late_10_count / float(observed_delivered)) * 100.0, 2)},
        {"stakeholder": "VP Operations (All Orders)", "formula": "delay > 0m on 1,600 population", "rate": round((late_count / float(total_orders)) * 100.0, 2)},
        {"stakeholder": "Finance (Settled Revenue)", "formula": "Delivered orders only", "rate": round((late_count / float(observed_delivered)) * 100.0, 2)},
    ]
    return comparison
