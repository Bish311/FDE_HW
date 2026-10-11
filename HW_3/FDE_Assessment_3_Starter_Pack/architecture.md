# Architecture Specification: AI Procurement Request Copilot

**Author:** BISHWAYAN CHATTERJEE -- 10200  
**Date:** October 11, 2026  
**System:** AI Procurement Request Copilot  
**Version:** 2.0 (Production Architecture A)

---

## 1. High-Level System Architecture

The AI Procurement Request Copilot operates under a **Deterministic-First, Hybrid Model Gating** paradigm. Pure algorithmic code strictly enforces procurement policy rules, financial thresholds, and security triggers, while lightweight System-One classification models (`inception/mercury-decide:free`) provide instant risk gating, and reasoning LLMs (`openai/gpt-6-luna`) draft contextual stakeholder communication.

```mermaid
flowchart TD
    subgraph Client ["Frontend Presentation Layer"]
        UI["React 18 + TypeScript Dashboard<br/>Solid Dark Mode (#0d0f12)"]
        HForm["Human Review Form<br/>(Accept / Reject / Return / Override)"]
    end

    subgraph API ["FastAPI Application Gateway (:8000)"]
        ReqEP["/api/requests<br/>(Request Ingestion)"]
        EvalEP["/api/evaluate<br/>(Agent Execution)"]
        AuditEP["/api/audit<br/>(Immutable Log)"]
    end

    subgraph AgentLayer ["Copilot Agent Core"]
        Coord["Single Agent Orchestrator"]
        Ledger["Append-Only Evidence Ledger<br/>(E1, E2, E3, ...)"]
        Guard["Deterministic Decision Guardrail<br/>(Enforces Policy Floor)"]
    end

    subgraph Tools ["Deterministic Enterprise Tools"]
        T1["Requester Org Hierarchy Tool<br/>(employees.csv)"]
        T2["Department Budget Tool<br/>(department_budgets.csv)"]
        T3["Software Catalog Tool<br/>(software_catalog.csv)"]
        T4["Vendor Registry & Risk Client<br/>(vendors.csv + Mock API :8001)"]
    end

    subgraph HybridEngine ["Policy & Model Intelligence"]
        Policy["Deterministic Policy Engine<br/>(Procurement Rules §1–§11)"]
        Mercury["System-One Decision Classifier<br/>(inception/mercury-decide:free)"]
        Luna["Generative Synthesis Engine<br/>(openai/gpt-6-luna)"]
    end

    UI --> ReqEP
    UI --> EvalEP
    HForm --> AuditEP

    EvalEP --> Coord
    Coord --> T1
    Coord --> T2
    Coord --> T3
    Coord --> T4

    T1 --> Ledger
    T2 --> Ledger
    T3 --> Ledger
    T4 --> Ledger

    Ledger --> Mercury
    Mercury --> Policy
    Ledger --> Policy
    Policy --> Luna
    Luna --> Guard
    Guard --> EvalEP
    EvalEP --> UI
```

---

## 2. End-to-End Request Evaluation Sequence

Every procurement request undergoes a 5-stage verification sequence with full telemetry logging and non-negotiable guardrails.

```mermaid
sequenceDiagram
    autonumber
    actor User as Procurement Reviewer<br/>(BISHWAYAN CHATTERJEE -- 10200)
    participant UI as React Dashboard
    participant API as FastAPI Backend (:8000)
    participant Agent as SingleProcurementAgent
    participant Tools as Enterprise Tools & Mock API
    participant Ledger as Evidence Ledger
    participant Mercury as Inception Mercury Decide
    participant Engine as Policy Engine (§1-§11)
    participant Luna as GPT-6 Luna
    participant Guard as Decision Guardrail

    User->>UI: Selects Request (e.g., REQ-1002) & Clicks "Evaluate"
    UI->>API: POST /api/evaluate {request_id: "REQ-1002", architecture: "single"}
    API->>Agent: run(request_id)
    
    Agent->>Tools: Query Org Hierarchy, Budget, Catalog, Vendor Risk
    Tools-->>Ledger: Append verified findings (E1..E5)
    
    Agent->>Mercury: POST /api/alpha/decisions (Batched Overlap + Injection Check)
    Mercury-->>Ledger: Record classifier confidence & decision (E6, E7)
    
    Agent->>Engine: evaluate(request, budget, vendor, catalog)
    Engine-->>Agent: PolicyReceipt (Required Approvals, Risk Flags, Route)
    
    Agent->>Luna: Synthesize recommendation & next-step copy
    Luna-->>Guard: Proposed Copy & Approvals
    
    Guard->>Guard: Enforce Policy Floor (Strict Supersize, Never Drop Approvals/Flags)
    Guard-->>API: ProcurementDecision Contract
    API-->>UI: Structured Response (Evidence Panel, Risk Flags, Actions)
    UI-->>User: Render Decision & Enable Human Review Form
```

---

## 3. Architecture Comparison: Single Agent vs. Staged Two-Agent

The project evaluated two architectural paradigms head-to-head on an identical test harness:

```mermaid
flowchart LR
    subgraph ArchA ["Architecture A: Single Agent Baseline (Selected)"]
        direction TB
        A_In["Procurement Request"] --> A_Agent["Unified Agent Orchestrator"]
        A_Agent --> A_Tools["Tool Gathering<br/>(4 Tools)"]
        A_Tools --> A_Ledger["Evidence Ledger"]
        A_Ledger --> A_Gating["Mercury Decide<br/>(Batched Gating)"]
        A_Gating --> A_Policy["Policy Engine (§1-§11)"]
        A_Policy --> A_Luna["GPT-6 Luna Synthesis"]
        A_Luna --> A_Guard["Decision Guardrail"]
        A_Guard --> A_Out["Final Procurement Decision<br/>(Avg Latency: 4,628 ms | 100% Pass)"]
    end

    subgraph ArchB ["Architecture B: Staged Two-Agent Pipeline"]
        direction TB
        B_In["Procurement Request"] --> B_Agent1["Agent 1: Procurement Analyst"]
        B_Agent1 --> B_Tools["Tool Gathering<br/>(4 Tools)"]
        B_Tools --> B_Handoff["Evidence Pack Serialization<br/>(Inter-Agent State Handoff)"]
        B_Handoff --> B_Agent2["Agent 2: Policy Reviewer"]
        B_Agent2 --> B_Gating["Mercury Decide<br/>(Batched Gating)"]
        B_Gating --> B_Policy["Policy Engine (§1-§11)"]
        B_Policy --> B_Luna["GPT-6 Luna Synthesis"]
        B_Luna --> B_Guard["Decision Guardrail"]
        B_Guard --> B_Out["Final Procurement Decision<br/>(Avg Latency: 5,182 ms | 100% Pass)"]
    end
```

### Architectural Trade-Off Analysis

| Dimension | Architecture A (Single Agent) | Architecture B (Staged Two-Agent) | Engineering Verdict |
|---|---|---|---|
| **Compliance Pass Rate** | **100.0% (18/18)** | **100.0% (18/18)** | **Tie**: Safety is enforced by code, not agents. |
| **Average Latency** | **4,628.2 ms** | **5,182.4 ms** | **Arch A is 10.7% faster** (zero handoff delay). |
| **p95 Latency** | **5,222.2 ms** | **5,935.6 ms** | **Arch A is 12.0% faster** in high-variance runs. |
| **Failure Surface** | In-memory execution trace | JSON serialization & schema drift | **Arch A**: Eliminates inter-agent failure points. |
| **Telemetry & Audit** | Single unified `RunTelemetry` trace | Split traces requiring correlation IDs | **Arch A**: Clean, single-pane observability. |

---

## 4. Deterministic Policy Engine (§1–§11) Workflow

The deterministic policy engine executes hard business rules that the generative model cannot alter or suppress:

```mermaid
flowchart TD
    Start["Request Ingested"] --> Tiers{"Annual Cost Tiers (§4)"}
    
    Tiers -->|"< $5,000"| M_App["Manager Approval"]
    Tiers -->|"$5k - $25,000"| DH_App["Department Head + Finance + Procurement"]
    Tiers -->|"$25k - $100,000"| VP_App["VP + Finance + Procurement"]
    Tiers -->|"> $100,000"| CFO_App["CFO + VP + Finance + Procurement"]

    Start --> BudgetCheck{"Budget Check (§2)"}
    BudgetCheck -->|"Insufficient"| BudgetFlag["Flag: budget_insufficient<br/>Add Approval: Finance"]
    BudgetCheck -->|"Sufficient"| CatalogCheck{"Catalog Overlap (§3)"}

    CatalogCheck -->|"Overlap Found"| OverlapFlag["Flag: existing_tool_overlap<br/>Run Mercury Overlap Classifier"]
    CatalogCheck -->|"No Overlap"| SecurityCheck{"Security Triggers (§5)"}

    SecurityCheck -->|"Customer/Source Data or Expired Vendor"| SecFlag["Flag: security_review_required<br/>Add Approval: Security"]
    SecurityCheck -->|"Standard Data"| PrivacyCheck{"Privacy Triggers (§6)"}

    PrivacyCheck -->|"Customer PII / Sensitive HR Data"| PrivFlag["Flag: privacy_review_required<br/>Add Approval: Privacy"]
    PrivacyCheck -->|"Standard"| LegalCheck{"Legal Triggers (§7)"}

    LegalCheck -->|"New Vendor or Cost > $50,000"| LegFlag["Flag: legal_review_required<br/>Add Approval: Legal"]
    LegalCheck -->|"Established Vendor"| InjectionCheck{"Prompt Injection Check (§11)"}

    InjectionCheck -->|"Adversarial Pattern Detected"| InjFlag["Flag: prompt_injection_detected<br/>Route: escalate_security_review"]
    InjectionCheck -->|"Safe Input"| RouteCalc["Calculate Final Routing"]

    RouteCalc --> FinalReceipt["Assemble Immutable PolicyReceipt"]
```

---

## 5. Human-in-the-Loop Governance & Audit Trail

The copilot strictly respects human authority. Autonomous purchasing is disabled; `human_review_required` is permanently locked to `true`.

```mermaid
flowchart LR
    Rec["Copilot Decision & Evidence"] --> Reviewer["Human Reviewer<br/>(BISHWAYAN CHATTERJEE -- 10200)"]
    
    Reviewer --> ActionChoice{"Select Decision"}
    
    ActionChoice -->|Accept| Act1["Accept Recommendation<br/>(Proceeds to standard route)"]
    ActionChoice -->|Reject| Act2["Reject Request<br/>(Terminates with written rationale)"]
    ActionChoice -->|Return| Act3["Return for Clarification<br/>(Prompts requester for missing data)"]
    ActionChoice -->|Override| Act4["Human Override<br/>(Overrides policy with audit explanation)"]

    Act1 --> Ledger["Append-Only Audit Ledger (:8000/api/audit)"]
    Act2 --> Ledger
    Act3 --> Ledger
    Act4 --> Ledger

    Ledger --> Persist["Persistent CSV Log<br/>(timestamp, user, action, rationale)"]
```

---

## 6. System Specifications & Port Mapping

| Component | Technology | Port / Host | Purpose |
|---|---|---|---|
| **Mock Vendor-Risk API** | FastAPI / Uvicorn | `http://127.0.0.1:8001` | External vendor risk scoring service |
| **Backend Copilot API** | FastAPI / Uvicorn | `http://127.0.0.1:8000` | Tool runner, policy engine, evaluation API |
| **Frontend Dashboard** | React 18, Vite, TypeScript | `http://localhost:5173` | Human reviewer dashboard (Dark Mode) |
| **Classifier Model** | `inception/mercury-decide:free` | OpenRouter Decisions API | System-One rapid gating for overlap & security |
| **Reasoning Model** | `openai/gpt-6-luna` (medium) | OpenRouter Chat API | Contextual copy synthesis & justification drafting |
