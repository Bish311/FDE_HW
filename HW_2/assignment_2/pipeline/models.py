from typing import TypedDict, Optional, List, Dict, Any

class OrderRecord(TypedDict):
    order_id: str
    customer_id: str
    restaurant_id: str
    driver_id: str
    city: str
    created_at: str
    promised_eta: str
    pickup_at: Optional[str]
    actual_delivery_at: Optional[str]
    final_status: str
    distance_km_estimate: float
    traffic_bucket: str
    weather_bucket: str

class QuarantineItem(TypedDict):
    order_id: str
    reason: str
    severity: str
    record_payload: Dict[str, Any]

class ValidationVerdict(TypedDict):
    business_grain: str
    timestamp_chronology: str
    kpi_definition: str
    category_semantics: str
    cross_source_mapping: str
    freshness: str
    publish_56_percent: str

class ScorecardMetrics(TypedDict):
    total_orders: int
    delivered_orders_observed: int
    unrecorded_deliveries: int
    cancelled_orders: int
    leadership_late_rate_percent: float
    support_operational_late_rate_percent: float
    severe_delay_rate_percent: float
    customer_escalation_rate_percent: float
    proactive_intervention_rate_percent: float
    order_cancellation_rate_percent: float

class IngestSummary(TypedDict):
    sqlite_orders: int
    sqlite_customers: int
    sqlite_drivers: int
    sqlite_restaurants: int
    dispatch_orders: int
    driver_events: int
    support_tickets: int
    customer_actions: int
    interventions: int
    outcomes: int
