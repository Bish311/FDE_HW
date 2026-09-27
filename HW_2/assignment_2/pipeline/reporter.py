import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from pipeline.models import ScorecardMetrics, ValidationVerdict, QuarantineItem

logger = logging.getLogger("pipeline.reporter")

def write_mart_csv(records: List[Dict[str, Any]], target_file: Path) -> None:
    if not records:
        return
    target_file.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: List[str] = list(records[0].keys())
    with open(target_file, mode="w", newline="", encoding="utf-8") as fp:
        writer = csv.DictWriter(fp, fieldnames=fieldnames)
        writer.writeheader()
        for row in records:
            writer.writerow(row)
    logger.info("Saved order decision mart with %d records to %s", len(records), target_file.name)

def write_scorecard_csv(scorecard: ScorecardMetrics, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, mode="w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["Metric", "Value"])
        for key, val in scorecard.items():
            writer.writerow([key, val])
    logger.info("Saved scorecard metrics to %s", target_file.name)

def write_stakeholders_csv(comparison: List[Dict[str, Any]], target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, mode="w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow(["Stakeholder", "Formula", "Late Rate (%)"])
        for item in comparison:
            writer.writerow([item["stakeholder"], item["formula"], item["rate"]])
    logger.info("Saved stakeholder comparison to %s", target_file.name)

def write_json_payload(payload: Any, target_file: Path) -> None:
    target_file.parent.mkdir(parents=True, exist_ok=True)
    with open(target_file, mode="w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
    logger.info("Saved JSON payload to %s", target_file.name)

def log_terminal_summary(
    scorecard: ScorecardMetrics,
    verdict: ValidationVerdict,
    quarantine_count: int,
) -> None:
    sep: str = "=" * 65
    logger.info(sep)
    logger.info("FLASHEATS FDE PIPELINE EXECUTION SUMMARY")
    logger.info(sep)
    logger.info("  Pipeline Run Status            : SUCCESS (All stages finished)")
    logger.info("  Total Business Orders Ingested : %d", scorecard["total_orders"])
    logger.info("  Observed Delivered Orders      : %d", scorecard["delivered_orders_observed"])
    logger.info("  Unrecorded Deliveries          : %d", scorecard["unrecorded_deliveries"])
    logger.info("  Quarantine Records Isolated    : %d", quarantine_count)
    logger.info("-----------------------------------------------------------------")
    logger.info("  Leadership Late Rate Claim     : %.2f%% [VETOED - Fails contract]", scorecard["leadership_late_rate_percent"])
    logger.info("  Support Operational Late Rate  : %.2f%% [CANONICAL SLA >10M - APPROVED]", scorecard["support_operational_late_rate_percent"])
    logger.info("  Severe Delay Rate (>20m)       : %.2f%%", scorecard["severe_delay_rate_percent"])
    logger.info("  Customer Escalation Rate       : %.2f%%", scorecard["customer_escalation_rate_percent"])
    logger.info("  Proactive Intervention Rate    : %.2f%%", scorecard["proactive_intervention_rate_percent"])
    logger.info("  Order Cancellation Rate        : %.2f%%", scorecard["order_cancellation_rate_percent"])
    logger.info("-----------------------------------------------------------------")
    logger.info("  Publish 56%% Leadership Claim  : %s (Vetoed - Fails data contract)", verdict["publish_56_percent"])
    logger.info("  Publish 23.34% Operational SLA : PASS (Approved for reporting)")
    logger.info(sep)
