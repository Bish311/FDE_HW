from datetime import datetime, timezone
import logging
import sys
from typing import List, Dict, Any
import config
from pipeline.ingest_db import fetch_sqlite_orders, fetch_sqlite_table
from pipeline.ingest_api import fetch_dispatch_orders
from pipeline.ingest_files import read_csv_records, read_driver_events
from pipeline.validate_contract import run_contract_audit
from pipeline.validate_gate import audit_restaurant_freshness, evaluate_validation_gate
from pipeline.transform_dims import build_dim_customers, build_dim_restaurants, build_dim_drivers
from pipeline.transform_mart import build_order_mart
from pipeline.metrics_calc import calculate_scorecard, calculate_stakeholder_comparison
from pipeline.reporter import write_mart_csv, write_scorecard_csv, write_stakeholders_csv, write_json_payload, log_terminal_summary

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
logger = logging.getLogger("main")

def run_pipeline() -> int:
    logger.info("Initializing FlashEats Dependable FDE Pipeline (Engineer: %s)", config.ENGINEER_PERSONA)
    logger.info("[STAGE 1/4: INGESTION] Extracting multi-modal sources across SQL, API, and files...")
    raw_orders = fetch_sqlite_orders(config.DB_PATH)
    raw_customers = fetch_sqlite_table(config.DB_PATH, "customers")
    raw_drivers = fetch_sqlite_table(config.DB_PATH, "drivers")
    raw_restaurants = fetch_sqlite_table(config.DB_PATH, "restaurants")
    dispatch_records = fetch_dispatch_orders(
        config.API_ENDPOINT, config.API_CACHE_DIR, config.API_MAX_PAGES, config.API_PAGE_SIZE, config.API_EXPECTED_TOTAL
    )
    support_tickets = read_csv_records(config.DATA_DIR / "support_tickets.csv")
    app_actions = read_csv_records(config.DATA_DIR / "customer_app_actions.csv")
    interventions = read_csv_records(config.DATA_DIR / "order_interventions.csv")
    outcomes = read_csv_records(config.DATA_DIR / "order_outcomes.csv")
    restaurant_status = read_csv_records(config.DATA_DIR / "restaurant_status.csv")
    driver_events = read_driver_events(config.DATA_DIR / "driver_events.json")

    logger.info("[STAGE 2/4: VALIDATION] Auditing 5-point contract, quarantine isolation, and freshness SLA...")
    clean_orders, quarantine_items, contract_stats = run_contract_audit(raw_orders)
    freshness_stats = audit_restaurant_freshness(clean_orders, restaurant_status)
    verdict = evaluate_validation_gate(contract_stats, freshness_stats)

    logger.info("[STAGE 3/4: MODELING] Reconstructing workflow entities, dimensions, and decision mart...")
    dim_customers = build_dim_customers(raw_customers)
    dim_restaurants = build_dim_restaurants(raw_restaurants)
    dim_drivers = build_dim_drivers(raw_drivers)
    mart_records = build_order_mart(clean_orders, app_actions, interventions, outcomes)

    logger.info("[STAGE 4/4: PUBLICATION] Generating scorecard, stakeholder matrix, and audit artifacts...")
    scorecard = calculate_scorecard(mart_records)
    stakeholders = calculate_stakeholder_comparison(mart_records)

    write_mart_csv(mart_records, config.MARTS_DIR / "fact_order_mart.csv")
    write_scorecard_csv(scorecard, config.METRICS_DIR / "metrics_scorecard.csv")
    write_stakeholders_csv(stakeholders, config.METRICS_DIR / "stakeholder_comparison.csv")
    write_json_payload(quarantine_items, config.VALIDATION_DIR / "quarantine_orders.json")

    validation_report_payload: Dict[str, Any] = {
        "verdict": verdict,
        "contract_statistics": contract_stats,
        "freshness_statistics": freshness_stats,
        "stakeholder_comparison": stakeholders,
    }
    write_json_payload(validation_report_payload, config.VALIDATION_DIR / "validation_report.json")

    run_report_payload: Dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "engineer": config.ENGINEER_PERSONA,
        "status": "COMPLETED",
        "ingest_audit": {
            "sqlite_orders": len(raw_orders),
            "clean_orders": len(clean_orders),
            "dispatch_api_orders": len(dispatch_records),
            "support_tickets": len(support_tickets),
            "customer_actions": len(app_actions),
            "interventions": len(interventions),
            "outcomes": len(outcomes),
            "courier_profiles": len(driver_events),
        },
        "scorecard": scorecard,
        "validation_verdict": verdict,
    }
    write_json_payload(run_report_payload, config.AUDIT_DIR / "pipeline_run_report.json")
    log_terminal_summary(scorecard, verdict, len(quarantine_items))
    return 0

if __name__ == "__main__":
    sys.exit(run_pipeline())
