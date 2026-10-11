export interface PurchaseRequest {
  request_id: string;
  requester_id: string;
  product_name: string;
  vendor_name: string;
  category: string;
  annual_cost_usd: number | null;
  user_count: number | null;
  business_justification: string | null;
  data_access_level: string | null;
  requested_integrations: string[];
  urgency?: string;
  department?: string;
}

export interface EvidenceItem {
  source: string;
  finding: string;
  reference: string | null;
}

export interface RunTelemetry {
  llm_calls: number | null;
  tool_calls: number | null;
  tool_names: string[];
}

export interface ProcurementDecision {
  request_id: string;
  recommendation: string;
  evidence: EvidenceItem[];
  required_approvals: string[];
  missing_information: string[];
  risk_flags: string[];
  next_step: string;
  human_review_required: boolean;
  telemetry: RunTelemetry | null;
}

export interface HumanAuditEntry {
  timestamp: string;
  request_id: string;
  reviewer: string;
  action: "accept" | "reject" | "return" | "override";
  justification: string;
  decision_summary?: Record<string, unknown>;
}

export type ArchitectureChoice = "single" | "staged" | "rules";
