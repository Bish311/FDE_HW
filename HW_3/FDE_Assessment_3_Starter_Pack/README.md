# AI Procurement Request Copilot

**Author:** BISHWAYAN CHATTERJEE -- 10200  
**Project:** FDE Assessment 3 - AI Procurement Request Copilot  

---

## 1. Summary

The AI Procurement Request Copilot is an automated enterprise workflow system designed to evaluate employee software purchasing requests. The system automatically inspects organizational reporting lines, validates costs against departmental budgets, checks for duplicate software in the enterprise catalog, and verifies vendor risk compliance. Every evaluated request generates structured recommendations, flags policy triggers, and routes the request for mandatory human review and audit logging.

---

## 2. Quick Start

### Environment Configuration
Before starting the application, copy the example environment file and set your credentials:

```bash
# On Windows (PowerShell)
Copy-Item .env.example .env

# On Linux / macOS
cp .env.example .env
```

Set your `OPENROUTER_API_KEY` inside `.env`.

### Running the System
The full stack (FastAPI Backend, Mock Vendor-Risk API, and React Frontend) starts with a single command:

```bash
# On Windows
python run_local.py

# On Linux / macOS
./start.sh
```

### Services and Ports
- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://127.0.0.1:8000 (API documentation at http://127.0.0.1:8000/docs)
- **Mock Vendor-Risk Service:** http://127.0.0.1:8001

### Running Tests and Evaluations
```bash
# Run pre-flight environment checks
python verify_setup.py

# Run unit tests
pytest -v

# Run public benchmark evaluations
python evals/run_public_evals.py --architecture single
python evals/run_public_evals.py --architecture staged

# Run comparative benchmark harness
python reports/test_compare.py

# Run linter
ruff check src/ tests/ evals/ reports/
```

---

## 3. System Architecture

The application is structured into four main layers:

1. **Frontend Dashboard:** React 18 and TypeScript interface providing request details, an evidence panel, risk flag highlights, and an interactive human review form.
2. **Backend Application:** FastAPI service exposing endpoints for request ingestion (`/api/requests`), request evaluation (`/api/evaluate`), and audit logging (`/api/audit`).
3. **Data Retrieval Tools:** Automated integrations that query employee data (`employees.csv`), department budgets (`department_budgets.csv`), software catalog records (`software_catalog.csv`), and vendor risk data (`vendors.csv` and the mock vendor-risk endpoint).
4. **Evaluation Engine:** Validates financial thresholds, catalog overlaps, and security requirements, using classification gating and generative copy synthesis before packaging the final decision.

For full architectural diagrams and sequence flowcharts, see [architecture.md](architecture.md).

---

## 4. Architecture Comparison and Evaluation

The system implements and compares two architectural designs:
- **Architecture A (Single Agent):** A unified pipeline executing data retrieval, classification gating, policy evaluation, and output generation within a single execution trace.
- **Architecture B (Staged Two-Agent):** A two-stage pipeline separating data gathering (Procurement Analyst) from compliance review (Policy Reviewer) via an explicit state handoff.

### Benchmark Results

Benchmarked across the standardized test suite with live model execution:

| Metric | Architecture A (Single Agent) | Architecture B (Staged Two-Agent) | Comparison |
|---|---|---|---|
| Benchmark Pass Rate | 100.0% (6 / 6) | 100.0% (6 / 6) | Equal |
| Full Suite Pass Rate | 100.0% (18 / 18) | 100.0% (18 / 18) | Equal |
| Average Latency | 4,628.2 ms | 5,182.4 ms | Architecture A is 10.7% faster |
| p95 Latency | 5,222.2 ms | 5,935.6 ms | Architecture A is 12.0% faster |
| Tool Calls per Request | 4 | 4 | Equal |
| Model Calls per Request | 2 | 2 | Equal |
| Inter-Agent Handoffs | 0 | 1 | Architecture A has zero handoff overhead |

For the full comparative evaluation report, see [reports/report.md](reports/report.md).  
For the benchmark script and raw data, see [reports/test_compare.py](reports/test_compare.py) and [reports/comparison_benchmark.csv](reports/comparison_benchmark.csv).

---

## 5. Production Decision

### Selected: Architecture A (Single Agent)

Architecture A is selected for production deployment for the following reasons:
1. **Safety Parity:** Both architectures achieve an identical 100% pass rate across all evaluated cases.
2. **Lower Latency:** Architecture A executes with 10.7% lower average latency and 12.0% lower p95 latency by eliminating state serialization between stages.
3. **Operational Simplicity:** A single execution trace simplifies logging, error tracking, and maintenance.

For the formal executive decision memo, see [docs/DECISION_MEMO.md](docs/DECISION_MEMO.md).

---

## 6. Human Review and Audit Logging

Every procurement recommendation is advisory and requires human confirmation (`human_review_required = True`). 

Authorized reviewers can perform four actions from the dashboard:
- **Accept:** Approve the recommendation and send the request to its required approval route.
- **Reject:** Deny the request with written justification.
- **Return:** Send the request back to the employee for missing information.
- **Override:** Override the standard recommendation with documented rationale.

All human review actions are logged to `audit_ledger.csv` with timestamp, reviewer ID (`BISHWAYAN CHATTERJEE -- 10200`), action type, and notes.
