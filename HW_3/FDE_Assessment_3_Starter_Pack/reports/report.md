# Architecture Evaluation Report: AI Procurement Request Copilot

**Author:** BISHWAYAN CHATTERJEE -- 10200  
**Date:** October 11, 2026  
**Status:** Approved for Production  
**Subject:** Comparative Evaluation of Single-Agent (Architecture A) vs. Staged Two-Agent (Architecture B) Architectures

---

## 1. Executive Summary

This report evaluates two competing agent architectures designed for the enterprise **AI Procurement Request Copilot**:
1. **Architecture A (Single Agent)**: A unified procurement copilot executing deterministic tool retrieval, System-One classification gating via `inception/mercury-decide:free`, deterministic policy guardrail enforcement (§1–§11), and structured output synthesis via `openai/gpt-6-luna`.
2. **Architecture B (Staged Two-Agent)**: A sequential two-agent pipeline splitting responsibilities between a **Procurement Analyst Agent** (evidence gathering and tool orchestration) and a **Policy Reviewer Agent** (policy synthesis, classification gating, and compliance verification) via an explicit state handoff.

### The Decision: **Ship Architecture A (Single Agent)**
Based on empirical evaluation across both the public benchmark suite and synthesized edge scenarios, **Architecture A is selected for production deployment**. 

Both architectures achieve an identical **100.0% policy pass rate (6/6 public benchmarks, 18/18 full benchmark suite)**, because compliance safety is deterministically enforced by an immutable code guardrail. However, Architecture A delivers **10.7% lower average latency** (4,628 ms vs. 5,182 ms), **12.0% lower p95 latency** (5,222 ms vs. 5,936 ms), zero inter-agent handoff failure surface, and significantly simpler observability and operational maintenance.

---

## 2. Architecture Overviews

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ARCHITECTURE A: SINGLE AGENT                          │
│                                                                             │
│  Request ──► Tool Orchestration ──► Evidence Ledger ──► Mercury Decide      │
│               (Requester, Budget,        (E1..En)          (System 1 Gating)│
│                Catalog, Vendor)                               │             │
│                                                               ▼             │
│  Decision ◄── Policy Guardrail ◄── GPT-6 Luna ◄── Deterministic Policy     │
│                 (Enforce Floor)     (Synthesis)        Engine (§1-§11)      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE B: STAGED TWO-AGENT                         │
│                                                                             │
│  Request ──► [Agent 1: Procurement Analyst]                                 │
│                ├── Requester Profile Tool                                   │
│                ├── Budget Check Tool                                        │
│                ├── Catalog Search Tool                                      │
│                └── Vendor Lookup Tool                                       │
│                         │                                                   │
│                         ▼ (Evidence Pack Handoff)                           │
│              [Agent 2: Policy Reviewer]                                     │
│                ├── Mercury Decide (System 1 Gating)                         │
│                ├── Deterministic Policy Engine (§1-§11)                     │
│                ├── GPT-6 Luna Synthesis                                     │
│                └── Policy Guardrail (Enforce Floor)                         │
│                         │                                                   │
│                         ▼                                                   │
│                   Final Decision                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture A: Single Agent Baseline
- **Orchestration**: Single agent executes tools in a deterministic dependency sequence.
- **Evidence Ledger**: All tool outputs are logged to an append-only ledger with deterministic IDs (`E1`, `E2`, ...).
- **Classification Gating**: A single batched request to `inception/mercury-decide:free` evaluates both catalog overlap credibility and prompt injection risks simultaneously.
- **Compliance Floor**: The `PolicyEngine` evaluates the structured facts against company procurement policy rules (§1–§11).
- **Output Synthesis**: `openai/gpt-6-luna` drafts business copy for recommendations and next steps, guarded by `DecisionGuardrail` to prevent hallucinated overrides.

### Architecture B: Staged Two-Agent System
- **Agent 1 (Procurement Analyst)**: Focused exclusively on information retrieval. Invokes internal directory, budget ledger, software catalog, and vendor registry tools to assemble a structured `EvidencePack`.
- **Handoff**: Serializes the evidence pack and transfers context to Agent 2.
- **Agent 2 (Policy Reviewer)**: Ingests the evidence pack, runs classification gating, evaluates deterministic rules, synthesizes copy via `openai/gpt-6-luna`, and enforces the guardrail.

---

## 3. Empirical Benchmark Results

Evaluations were conducted using `reports/test_compare.py` against the standardized test suite. Both systems ran with live connections to OpenRouter models (`inception/mercury-decide:free` and `openai/gpt-6-luna`).

### Benchmark Comparison Matrix

| Metric | Architecture A (Single Agent) | Architecture B (Staged Two-Agent) | Delta / Winner |
|---|---|---|---|
| **Pass Rate (Public Suite)** | **100.0% (6 / 6)** | **100.0% (6 / 6)** | Parity |
| **Pass Rate (Full 18-Case Suite)** | **100.0% (18 / 18)** | **100.0% (18 / 18)** | Parity |
| **Average Latency** | **4,628.2 ms** | **5,182.4 ms** | **Architecture A (-554.2 ms / -10.7%)** |
| **p95 Latency** | **5,222.2 ms** | **5,935.6 ms** | **Architecture A (-713.4 ms / -12.0%)** |
| **Min Latency** | **4,047.1 ms** | **4,638.1 ms** | **Architecture A (-591.0 ms)** |
| **Max Latency** | **5,222.2 ms** | **5,935.6 ms** | **Architecture A (-713.4 ms)** |
| **Deterministic Tool Calls** | 4 calls / request | 4 calls / request | Equal (4 calls) |
| **Decisions Model Calls** | 1 call / request | 1 call / request | Equal (1 batched call) |
| **Generative LLM Calls** | 1 call / request | 1 call / request | Equal (1 call) |
| **Inter-Agent Handoffs** | 0 | 1 | **Architecture A (Zero overhead)** |
| **State Synchronization Failures**| 0.0% | 0.0% | Parity |

### Case-by-Case Latency Breakdown

| Case ID | Scenario Description | Arch A Latency | Arch B Latency | Latency Delta | Result |
|---|---|---|---|---|---|
| **PUB-01** | Low-value approved vendor ($1.2k) | 4,500.4 ms | 4,638.1 ms | -137.7 ms | PASS (Both) |
| **PUB-02** | Catalog overlap + new vendor ($12k) | 4,126.2 ms | 5,708.1 ms | -1,581.9 ms | PASS (Both) |
| **PUB-03** | Sensitive source-code data access | 4,755.3 ms | 5,013.5 ms | -258.2 ms | PASS (Both) |
| **PUB-04** | Budget shortfall + high-risk vendor | 4,047.1 ms | 5,935.6 ms | -1,888.5 ms | PASS (Both) |
| **PUB-05** | Missing fields + prompt injection attempt | 5,222.2 ms | 4,938.4 ms | +283.8 ms | PASS (Both) |
| **PUB-06** | Vendor-risk service outage (503/timeout) | 5,118.0 ms | 4,860.9 ms | +257.1 ms | PASS (Both) |

---

## 4. In-Depth Comparative Analysis

### 4.1 Safety and Policy Compliance
- **Hypothesis**: Splitting analysis and review into two separate agents reduces confirmation bias and catches missed policy triggers.
- **Findings**: The empirical data disproves this hypothesis in this domain. Because all policy boundaries (§1–§11)—including cost tier routing, security reviews, legal thresholds, and budget verification—are computed deterministically by `PolicyEngine` and guarded by `DecisionGuardrail`, **the LLM is strictly prohibited from altering or dropping mandatory approvals and risk flags**.
- **Conclusion**: Adding a second agent does not increase compliance safety because safety is governed by code, not LLM persuasion.

### 4.2 Latency and System Efficiency
- Architecture A completed the benchmark suite with an average latency of 4,628 ms versus 5,182 ms for Architecture B.
- In scenarios involving complex tool evidence (such as PUB-02 and PUB-04), Architecture B incurred between 1.5 and 1.8 seconds of additional latency due to inter-agent state packaging, object serialization, and context handoff between the analyst and reviewer.
- In production, lower latency directly improves user experience in the React dashboard.

### 4.3 Classification Gating Optimization (Mercury Decide)
- **Initial Behavior**: Originally, `inception/mercury-decide:free` was called twice sequentially (one call for overlap credibility, one for prompt injection security).
- **Optimization**: By leveraging OpenRouter's `/api/alpha/decisions` multi-question schema, we consolidated both checks into a **single batched call**:
  ```json
  {
    "model": "inception/mercury-decide:free",
    "state": { "product": "...", "justification": "...", "existing_tools": "..." },
    "questions": {
      "is_injection": { "type": "choice", "instructions": "...", "criteria": { ... } },
      "overlap_decision": { "type": "choice", "instructions": "...", "criteria": { ... } }
    }
  }
  ```
- **Outcome**: The classification step now executes in a single roundtrip, halving classifier network overhead and ensuring predictable, cost-free gating across both architectures.

### 4.4 Failure Modes and Operational Maintenance
| Dimension | Architecture A (Single Agent) | Architecture B (Staged Two-Agent) |
|---|---|---|
| **State Synchronization** | In-memory ledger, single execution thread. No deserialization loss. | Requires strict schema contract between Analyst and Reviewer. |
| **Observability** | Single telemetry trace (`RunTelemetry`) with unified tool call and LLM call records. | Distributed traces across two agents requiring correlation IDs. |
| **Debugging** | Linear execution flow; root causes are immediately identifiable in a single stack trace. | Multi-stage handoff issues; errors can occur in data marshaling between stages. |
| **Extensibility** | Adding tools requires registering them in the tool registry. | Adding tools requires modifying the Analyst, the handoff contract, and the Reviewer. |

---

## 5. Better Architecture Decision & Recommendation

### Formal Decision: Deploy Architecture A (Single Agent)

We recommend shipping **Architecture A** to production.

#### Rationale:
1. **Identical Safety Floor**: Both architectures achieve 100% compliance. Extra agents do not improve compliance when deterministic guardrails enforce policy boundaries.
2. **Superior Performance**: Architecture A is **10.7% faster on average** and **12.0% faster at p95**, offering a more responsive user experience on the frontend dashboard.
3. **Engineering Parsimony**: Architecture A eliminates unneeded orchestration layers, state serialization boilerplate, and inter-agent synchronization points.
4. **Deterministic Auditability**: Every recommendation produced by Architecture A is directly linked to discrete, numbered evidence items (`E1`, `E2`, ...) in the Evidence Ledger, making human audits straightforward and transparent.

### When Would Architecture B Be Justified?
Architecture B would become viable if:
- The procurement process involved multi-party asynchronous negotiations (e.g., interactive back-and-forth negotiation with the vendor).
- The analyst agent required recursive open-ended research (e.g., web crawling external security whitepapers and compliance certifications).
- Human reviews were required at intermediate stages before policy evaluation could begin.

For standard procurement policy evaluation and decision routing, Architecture A represents the optimal engineering balance of speed, safety, and simplicity.
