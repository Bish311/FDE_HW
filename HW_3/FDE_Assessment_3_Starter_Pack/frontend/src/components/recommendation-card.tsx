import React from "react";
import { ProcurementDecision } from "../types/procurement.ts";
import { cleanLabel } from "../lib/format.ts";

interface RecommendationCardProps {
  decision: ProcurementDecision | null;
  onExecuteAnalysis: () => void;
  isRunning: boolean;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({
  decision,
  onExecuteAnalysis,
  isRunning,
}) => {
  return (
    <section style={{
      padding: "24px",
      borderBottom: "1px solid var(--border-subtle)",
      backgroundColor: "var(--bg-surface)",
    }}>
      <div style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: "20px",
      }}>
        <h3 style={{
          fontSize: "14px",
          fontWeight: 600,
          color: "var(--text-main)",
          textTransform: "uppercase",
          letterSpacing: "0.04em",
        }}>
          Copilot Verdict & Next Action
        </h3>
        <button
          onClick={onExecuteAnalysis}
          disabled={isRunning}
          style={{
            padding: "8px 18px",
            fontSize: "12px",
            fontWeight: 600,
            borderRadius: "4px",
            backgroundColor: isRunning ? "var(--bg-surface-subtle)" : "var(--accent-dry-wash)",
            color: "var(--text-main)",
            border: "1px solid var(--border-active)",
            opacity: isRunning ? 0.6 : 1,
          }}
        >
          {isRunning ? "Running Analysis..." : "Run Analysis"}
        </button>
      </div>

      {!decision ? (
        <div style={{
          padding: "24px",
          textAlign: "center",
          color: "var(--text-dim)",
          fontSize: "13px",
          border: "1px dashed var(--border-subtle)",
          borderRadius: "4px",
        }}>
          Click &quot;Run Analysis&quot; above to evaluate this request against procurement policy.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <div style={{
            padding: "16px",
            backgroundColor: "var(--bg-surface-subtle)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "4px",
            borderLeft: "4px solid var(--accent-dry-wash)",
          }}>
            <div style={{
              fontSize: "11px",
              color: "var(--text-dim)",
              textTransform: "uppercase",
              marginBottom: "4px",
            }}>
              Recommendation
            </div>
            <div style={{
              fontSize: "14px",
              fontWeight: 600,
              color: "var(--text-main)",
              lineHeight: 1.5,
            }}>
              {decision.recommendation}
            </div>

            <div style={{
              fontSize: "11px",
              color: "var(--text-dim)",
              textTransform: "uppercase",
              marginTop: "12px",
              marginBottom: "4px",
            }}>
              Next Step
            </div>
            <div style={{
              fontSize: "13px",
              color: "var(--text-muted)",
              lineHeight: 1.5,
            }}>
              {decision.next_step}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
            <div style={{
              padding: "14px",
              backgroundColor: "var(--bg-surface-subtle)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "4px",
            }}>
              <div style={{
                fontSize: "11px",
                color: "var(--text-dim)",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}>
                Required Approvals ({decision.required_approvals.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {decision.required_approvals.map((app, i) => (
                  <span
                    key={i}
                    style={{
                      fontSize: "11px",
                      padding: "4px 8px",
                      borderRadius: "3px",
                      backgroundColor: "var(--tag-bg)",
                      color: "var(--tag-text)",
                      border: "1px solid var(--border-subtle)",
                      fontFamily: "JetBrains Mono, monospace",
                    }}
                  >
                    {app}
                  </span>
                ))}
              </div>
            </div>

            <div style={{
              padding: "14px",
              backgroundColor: "var(--bg-surface-subtle)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "4px",
            }}>
              <div style={{
                fontSize: "11px",
                color: "var(--text-dim)",
                textTransform: "uppercase",
                marginBottom: "8px",
              }}>
                Risk Flags ({decision.risk_flags.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {decision.risk_flags.length === 0 ? (
                  <span style={{ fontSize: "12px", color: "var(--text-dim)" }}>
                    No policy risk flags triggered
                  </span>
                ) : (
                  decision.risk_flags.map((flg, i) => (
                    <span
                      key={i}
                      style={{
                        fontSize: "11px",
                        padding: "4px 8px",
                        borderRadius: "3px",
                        backgroundColor: "var(--warning-bg)",
                        color: "var(--warning-text)",
                        border: "1px solid var(--warning-border)",
                        fontFamily: "JetBrains Mono, monospace",
                      }}
                    >
                      {cleanLabel(flg)}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>

          {decision.missing_information.length > 0 && (
            <div style={{
              padding: "12px 14px",
              backgroundColor: "var(--bg-surface-subtle)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "4px",
            }}>
              <div style={{
                fontSize: "11px",
                color: "var(--text-dim)",
                textTransform: "uppercase",
                marginBottom: "6px",
              }}>
                Missing Information Items
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {decision.missing_information.map((item, i) => (
                  <span
                    key={i}
                    style={{
                      fontSize: "11px",
                      padding: "3px 8px",
                      borderRadius: "3px",
                      backgroundColor: "var(--bg-surface)",
                      color: "var(--text-muted)",
                      border: "1px solid var(--border-subtle)",
                    }}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {decision.telemetry && (
            <div style={{
              fontSize: "11px",
              color: "var(--text-dim)",
              fontFamily: "JetBrains Mono, monospace",
              display: "flex",
              gap: "16px",
            }}>
              <span>LLM Calls: {decision.telemetry.llm_calls ?? 0}</span>
              <span>Tool Calls: {decision.telemetry.tool_calls ?? 0}</span>
              <span>Human Review Required: {decision.human_review_required ? "YES" : "NO"}</span>
            </div>
          )}
        </div>
      )}
    </section>
  );
};
