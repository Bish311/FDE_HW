# Dependable Pipeline Architecture & Rerun Invariants

**Lead Forward Deployed Engineer:** BISHWAYAN CHATTERJEE -- 10200  
**Platform:** FlashEats Hyperlocal Delivery Infrastructure  
**Core Objective:** Turn ad-hoc analysis into a repeatable, production-grade pipeline (Ingest $\rightarrow$ Validate $\rightarrow$ Transform $\rightarrow$ Metric Output); guarantee idempotency; implement failure handling and quarantine.  

---

## 1. Production Pipeline Architecture

The pipeline is organized into four sequential, decoupled stages executed via `main.py`:

```
[Raw Data Sources: SQLite, REST API, JSON, CSVs]
                    │
                    ▼
           [Stage 1: INGESTION]
  ├── pipeline/ingest_db.py    (Extract SQLite tables)
  ├── pipeline/ingest_api.py   (Resilient REST client + disk fallback)
  └── pipeline/ingest_files.py (Parse CSVs and driver events)
                    │
                    ▼
           [Stage 2: VALIDATION]
  ├── pipeline/validate_contract.py (PK deduplication, chronology)
  ├── pipeline/validate_gate.py     (Freshness SLA, Gate verdict)
  └── output/validation/quarantine_orders.json (12 isolated records)
                    │
                    ▼
      [Stage 3: WORKFLOW MODELING]
  ├── pipeline/transform_dims.py (dim_customers, restaurants, drivers)
  └── pipeline/transform_mart.py (output/marts/fact_order_mart.csv)
                    │
                    ▼
      [Stage 4: METRICS & AUDIT]
  ├── pipeline/metrics_calc.py   (Scorecard & stakeholder comparison)
  ├── pipeline/reporter.py       (JSON receipts & terminal summary)
  └── output/metrics/metrics_scorecard.csv
```

---

## 2. Dependability Invariants

### A. Strict Idempotency
Executing `python main.py` multiple times on identical raw inputs produces **byte-identical output files** across all target directories:
- `output/marts/fact_order_mart.csv`
- `output/metrics/metrics_scorecard.csv`
- `output/metrics/stakeholder_comparison.csv`
- `output/validation/quarantine_orders.json`
- `output/validation/validation_report.json`

Zero state leaks exist across runs. All in-memory lookups are scoped strictly to the execution invocation.

### B. Failure Handling & Quarantine Isolation
Corrupted data is never silently dropped or imputed. Records failing data contracts are isolated into `output/validation/quarantine_orders.json` with complete diagnostic metadata:

```json
{
  "order_id": "O00120",
  "reason": "duplicate_primary_key",
  "severity": "WARN",
  "record_payload": { ... }
}
```

#### Quarantined Population (12 Records):
1. **Primary Key Duplicates (3 records):** `O00120`, `O00723`, `O01302` quarantined to protect business grain.
2. **Inverted Promised ETAs (4 records):** `O00101` through `O00104` (`promised_eta < created_at`).
3. **Pickup After Delivery Anomalies (5 records):** `O00051` through `O00055` (`pickup_at > actual_delivery_at`).

### C. Enterprise Output Structure
Outputs are structured into dedicated functional directories designed for enterprise consumption:
- `output/validation/`: Validation gate verdicts and quarantined records.
- `output/metrics/`: Executive scorecard and stakeholder comparison matrices.
- `output/marts/`: Dimension-enriched, order-level decision mart.
- `output/audit/`: Timestamped pipeline execution audit receipts (`pipeline_run_report.json`).

---

## 3. Execution & Verification

The pipeline executes via a single command:

```powershell
python HW_2/assignment_2/main.py
```

### Staged CLI Execution Output:
```
2026-09-27 22:31:13 [INFO] Initializing FlashEats Dependable FDE Pipeline (Engineer: BISHWAYAN CHATTERJEE -- 10200)
2026-09-27 22:31:13 [INFO] [STAGE 1/4: INGESTION] Extracting multi-modal sources across SQL, API, and files...
2026-09-27 22:31:13 [INFO] Extracted 1603 orders from SQLite
2026-09-27 22:31:14 [INFO] Loaded 1600 dispatch records from disk cache
2026-09-27 22:31:14 [INFO] Read 202 records from support_tickets.csv
2026-09-27 22:31:14 [INFO] [STAGE 2/4: VALIDATION] Auditing 5-point contract, quarantine isolation, and freshness SLA...
2026-09-27 22:31:14 [INFO] Contract audit completed. Clean orders: 1600, Quarantined events: 12
2026-09-27 22:31:14 [INFO] Validation Gate Evaluated: Final Publish Verdict = FAIL
2026-09-27 22:31:14 [INFO] [STAGE 3/4: MODELING] Reconstructing workflow entities, dimensions, and decision mart...
2026-09-27 22:31:14 [INFO] Transformed 1600 unified orders into decision mart
2026-09-27 22:31:14 [INFO] [STAGE 4/4: PUBLICATION] Generating scorecard, stakeholder matrix, and audit artifacts...
2026-09-27 22:31:14 [INFO] Saved order decision mart with 1600 records to fact_order_mart.csv
2026-09-27 22:31:14 [INFO] Saved scorecard metrics to metrics_scorecard.csv
2026-09-27 22:31:14 [INFO] Saved stakeholder comparison to stakeholder_comparison.csv
```
