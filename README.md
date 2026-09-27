# Forward Deployed Engineering (FDE) Repository

**Engineer:** BISHWAYAN CHATTERJEE -- 10200  
**GitHub Repository:** [https://github.com/Bish311/FDE_HW](https://github.com/Bish311/FDE_HW)  

---

## Repository Structure

This repository houses operational engineering systems, forensic data investigations, and dependable pipelines developed for field deployments.

```
FDE_hw/
├── HW_2/
│   ├── assignment_2/                      # FlashEats FDE Architecture & Dependable Pipeline
│   │   ├── main.py                        # Pipeline execution entrypoint
│   │   ├── config.py                      # Local configuration & business constants
│   │   ├── pipeline/                      # Modular pipeline engine (Ingest, Validate, Model, Publish)
│   │   ├── database/                      # Core SQLite database (flasheats.db)
│   │   ├── data/                          # Operational CSVs, JSON telemetry & raw dispatch cache
│   │   ├── output/                        # Structured enterprise outputs
│   │   │   ├── validation/                # Quarantine store & validation report
│   │   │   ├── metrics/                   # Scorecard & stakeholder comparison
│   │   │   ├── marts/                     # Order-level decision mart (fact_order_mart.csv)
│   │   │   └── audit/                     # Execution run receipts
│   │   ├── docs/                          # Comprehensive requirement documentation (01 to 07)
│   │   └── README.md                      # Complete system documentation & architectural specification
│   └── flasheats-classroom-pack/          # Raw reference classroom pack
└── README.md                              # Root repository overview
```

---

## Primary Project: FlashEats Dependable Data Pipeline

The core project is located in [`HW_2/assignment_2/`](HW_2/assignment_2):
- **Problem:** Client leadership reported a flawed claim that "56% of deliveries are late" and requested an expensive machine learning delay model.
- **FDE Audit:** Disproved the traffic hypothesis ($r = 0.010$, low traffic late rate 25.8%), identified kitchen delay as the root cause (67.8% of support complaints), and uncovered an attribution black hole in courier telemetry (zero restaurant arrival timestamps).
- **Dependable Pipeline:** Ingests multi-modal sources, isolates 12 corrupted records into quarantine without crashing, vetoes the 56% claim at the validation gate, and establishes the canonical **23.34% Operational SLA (>10m)**.

### Quickstart Execution
```powershell
python HW_2/assignment_2/main.py
```

### Complete System Documentation
For detailed architectural specifications, ER diagrams, 5-point data contract rules, and the 3-minute video presentation script, see:
👉 **[`HW_2/assignment_2/README.md`](HW_2/assignment_2/README.md)**
