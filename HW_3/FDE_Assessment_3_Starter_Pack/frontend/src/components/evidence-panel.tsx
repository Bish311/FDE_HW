import React from "react";
import { EvidenceItem } from "../types/procurement.ts";

interface EvidencePanelProps {
  evidence: EvidenceItem[];
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({ evidence }) => {
  return (
    <section style={{
      padding: "24px",
      borderBottom: "1px solid var(--border-subtle)",
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
          Evidence Panel ({evidence.length} items)
        </h3>
        <span style={{
          fontSize: "11px",
          color: "var(--text-dim)",
          fontFamily: "JetBrains Mono, monospace",
        }}>
          Verified Evidence
        </span>
      </div>

      {evidence.length === 0 ? (
        <div style={{
          padding: "20px",
          textAlign: "center",
          color: "var(--text-dim)",
          fontSize: "13px",
          border: "1px dashed var(--border-subtle)",
          borderRadius: "4px",
        }}>
          No evidence gathered yet. Click &quot;Run Analysis&quot; to execute agent tools.
        </div>
      ) : (
        <div style={{
          border: "1px solid var(--border-subtle)",
          borderRadius: "4px",
          overflow: "hidden",
        }}>
          <table style={{
            width: "100%",
            borderCollapse: "collapse",
            textAlign: "left",
            fontSize: "12px",
          }}>
            <thead>
              <tr style={{
                backgroundColor: "var(--bg-surface-subtle)",
                borderBottom: "1px solid var(--border-subtle)",
                color: "var(--text-dim)",
                textTransform: "uppercase",
                fontFamily: "JetBrains Mono, monospace",
                fontSize: "11px",
              }}>
                <th style={{ padding: "10px 14px", width: "90px" }}>ID</th>
                <th style={{ padding: "10px 14px", width: "180px" }}>Source</th>
                <th style={{ padding: "10px 14px" }}>Verified Finding</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((item, idx) => {
                const rowBg = idx % 2 === 0 ? "var(--bg-surface)" : "var(--bg-surface-subtle)";
                const refId = item.reference ? item.reference.split(":")[0] : `E${idx + 1}`;
                return (
                  <tr
                    key={idx}
                    style={{
                      backgroundColor: rowBg,
                      borderBottom: "1px solid var(--border-subtle)",
                    }}
                  >
                    <td style={{
                      padding: "10px 14px",
                      fontFamily: "JetBrains Mono, monospace",
                      fontWeight: 600,
                      color: "var(--text-main)",
                    }}>
                      {refId}
                    </td>
                    <td style={{
                      padding: "10px 14px",
                      color: "var(--text-muted)",
                      fontFamily: "JetBrains Mono, monospace",
                    }}>
                      {item.source}
                    </td>
                    <td style={{
                      padding: "10px 14px",
                      color: "var(--text-main)",
                      lineHeight: 1.5,
                    }}>
                      {item.finding}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
