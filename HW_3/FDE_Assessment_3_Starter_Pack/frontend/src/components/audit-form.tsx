import React, { useState } from "react";
import { HumanAuditEntry, ProcurementDecision } from "../types/procurement.ts";

interface AuditFormProps {
  requestId: string;
  decision: ProcurementDecision | null;
  onAuditSubmitted: (entry: HumanAuditEntry) => void;
}

export const AuditForm: React.FC<AuditFormProps> = ({
  requestId,
  decision,
  onAuditSubmitted,
}) => {
  const [action, setAction] = useState<"accept" | "reject" | "return" | "override">("accept");
  const [justification, setJustification] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim()) {
      setStatusMessage("Justification is mandatory for all human review decisions.");
      return;
    }

    setIsSubmitting(true);
    setStatusMessage(null);

    const payload = {
      request_id: requestId,
      reviewer: "Bish",
      action: action,
      justification: justification.trim(),
      decision_summary: decision ? {
        recommendation: decision.recommendation,
        risk_flags: decision.risk_flags,
      } : {},
    };

    try {
      const resp = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (resp.ok) {
        const data = await resp.json();
        onAuditSubmitted(data.entry as HumanAuditEntry);
        setJustification("");
        setStatusMessage("Decision recorded to immutable audit log.");
      } else {
        setStatusMessage("Failed to record decision.");
      }
    } catch {
      setStatusMessage("Network error recording audit action.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section style={{
      padding: "24px",
      backgroundColor: "var(--bg-surface)",
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "16px",
      }}>
        <h3 style={{
          fontSize: "14px",
          fontWeight: 600,
          color: "var(--text-main)",
          textTransform: "uppercase",
          letterSpacing: "0.04em",
        }}>
          Human Review & Sign-Off (Reviewer: Bish)
        </h3>
        <span style={{
          fontSize: "11px",
          color: "var(--text-dim)",
          fontFamily: "JetBrains Mono, monospace",
        }}>
          Mandatory Human Review
        </span>
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "14px" }}>
        <div>
          <label style={{
            fontSize: "11px",
            color: "var(--text-dim)",
            textTransform: "uppercase",
            display: "block",
            marginBottom: "6px",
          }}>
            Action Verdict
          </label>
          <div style={{ display: "flex", gap: "8px" }}>
            {(["accept", "reject", "return", "override"] as const).map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setAction(opt)}
                style={{
                  padding: "6px 14px",
                  fontSize: "12px",
                  fontWeight: 500,
                  borderRadius: "4px",
                  textTransform: "capitalize",
                  backgroundColor: action === opt ? "var(--bg-surface-active)" : "var(--bg-surface-subtle)",
                  color: action === opt ? "var(--text-main)" : "var(--text-muted)",
                  border: action === opt ? "1px solid var(--border-active)" : "1px solid var(--border-subtle)",
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label style={{
            fontSize: "11px",
            color: "var(--text-dim)",
            textTransform: "uppercase",
            display: "block",
            marginBottom: "6px",
          }}>
            Reviewer Justification (Mandatory)
          </label>
          <textarea
            value={justification}
            onChange={(e) => setJustification(e.target.value)}
            placeholder="Document rationale, policy section citations, or override details..."
            rows={3}
            style={{
              width: "100%",
              padding: "10px 12px",
              backgroundColor: "var(--bg-surface-subtle)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "4px",
              color: "var(--text-main)",
              fontSize: "13px",
              resize: "vertical",
            }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              padding: "8px 20px",
              fontSize: "12px",
              fontWeight: 600,
              borderRadius: "4px",
              backgroundColor: "var(--accent-dry-wash)",
              color: "var(--text-main)",
              border: "1px solid var(--border-active)",
              opacity: isSubmitting ? 0.6 : 1,
            }}
          >
            {isSubmitting ? "Recording..." : "Record Final Decision"}
          </button>
          {statusMessage && (
            <span style={{ fontSize: "12px", color: "var(--text-dim)", fontFamily: "JetBrains Mono, monospace" }}>
              {statusMessage}
            </span>
          )}
        </div>
      </form>
    </section>
  );
};
