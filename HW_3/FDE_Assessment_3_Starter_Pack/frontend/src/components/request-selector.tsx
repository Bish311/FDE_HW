import React from "react";
import { PurchaseRequest } from "../types/procurement.ts";
import { formatCurrency } from "../lib/format.ts";

interface RequestSelectorProps {
  requests: PurchaseRequest[];
  selectedId: string | null;
  onSelect: (requestId: string) => void;
}

export const RequestSelector: React.FC<RequestSelectorProps> = ({
  requests,
  selectedId,
  onSelect,
}) => {
  return (
    <nav style={{
      width: "280px",
      borderRight: "1px solid var(--border-subtle)",
      backgroundColor: "var(--bg-surface)",
      overflowY: "auto",
      display: "flex",
      flexDirection: "column",
    }}>
      <div style={{
        padding: "14px 16px",
        borderBottom: "1px solid var(--border-subtle)",
        fontSize: "11px",
        fontWeight: 600,
        textTransform: "uppercase",
        letterSpacing: "0.06em",
        color: "var(--text-dim)",
      }}>
        Inbound Requests ({requests.length})
      </div>
      <div>
        {requests.map((req) => {
          const isSelected = req.request_id === selectedId;
          return (
            <button
              key={req.request_id}
              onClick={() => onSelect(req.request_id)}
              style={{
                width: "100%",
                textAlign: "left",
                padding: "12px 16px",
                borderBottom: "1px solid var(--border-subtle)",
                backgroundColor: isSelected ? "var(--bg-surface-active)" : "transparent",
                borderLeft: isSelected ? "3px solid var(--accent-dry-wash)" : "3px solid transparent",
                display: "flex",
                flexDirection: "column",
                gap: "4px",
              }}
            >
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}>
                <span style={{
                  fontSize: "12px",
                  fontWeight: 600,
                  fontFamily: "JetBrains Mono, monospace",
                  color: isSelected ? "var(--text-main)" : "var(--text-muted)",
                }}>
                  {req.request_id}
                </span>
                <span style={{
                  fontSize: "11px",
                  color: "var(--text-dim)",
                  fontFamily: "JetBrains Mono, monospace",
                }}>
                  {formatCurrency(req.annual_cost_usd)}
                </span>
              </div>
              <div style={{
                fontSize: "13px",
                fontWeight: 500,
                color: isSelected ? "var(--text-main)" : "var(--text-muted)",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}>
                {req.product_name}
              </div>
              <div style={{
                fontSize: "11px",
                color: "var(--text-dim)",
              }}>
                {req.category}
              </div>
            </button>
          );
        })}
      </div>
    </nav>
  );
};
