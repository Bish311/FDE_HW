import React from "react";
import { HumanAuditEntry } from "../types/procurement.ts";
import { formatDate } from "../lib/format.ts";

interface AuditHistoryProps {
  entries: HumanAuditEntry[];
}

export const AuditHistory: React.FC<AuditHistoryProps> = ({ entries }) => {
  if (entries.length === 0) {
    return null;
  }

  return (
    <section style={{
      padding: "24px",
      borderTop: "1px solid var(--border-subtle)",
      backgroundColor: "var(--bg-surface)",
    }}>
      <h3 style={{
        fontSize: "13px",
        fontWeight: 600,
        color: "var(--text-main)",
        textTransform: "uppercase",
        letterSpacing: "0.04em",
        marginBottom: "12px",
      }}>
        Audit Trail ({entries.length} actions)
      </h3>

      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {entries.map((item, idx) => (
          <div
            key={idx}
            style={{
              padding: "10px 14px",
              backgroundColor: "var(--bg-surface-subtle)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "4px",
              fontSize: "12px",
            }}
          >
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: "4px",
              fontFamily: "JetBrains Mono, monospace",
            }}>
              <span style={{ fontWeight: 600, color: "var(--text-main)", textTransform: "uppercase" }}>
                {item.action} by {item.reviewer}
              </span>
              <span style={{ color: "var(--text-dim)" }}>
                {formatDate(item.timestamp)}
              </span>
            </div>
            <div style={{ color: "var(--text-muted)" }}>
              {item.justification}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
