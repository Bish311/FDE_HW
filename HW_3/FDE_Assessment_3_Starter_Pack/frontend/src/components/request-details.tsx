import React from "react";
import { PurchaseRequest } from "../types/procurement.ts";
import { formatCurrency } from "../lib/format.ts";

interface RequestDetailsProps {
  request: PurchaseRequest | null;
}

export const RequestDetails: React.FC<RequestDetailsProps> = ({ request }) => {
  if (!request) {
    return (
      <section style={{ padding: "24px", color: "var(--text-dim)" }}>
        Select a request from the sidebar to inspect details.
      </section>
    );
  }

  return (
    <section style={{
      padding: "24px",
      borderBottom: "1px solid var(--border-subtle)",
      backgroundColor: "var(--bg-surface)",
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        marginBottom: "20px",
      }}>
        <div>
          <div style={{
            fontSize: "11px",
            fontFamily: "JetBrains Mono, monospace",
            color: "var(--text-dim)",
            marginBottom: "4px",
          }}>
            {request.request_id}
          </div>
          <h2 style={{ fontSize: "18px", fontWeight: 600, color: "var(--text-main)" }}>
            {request.product_name}
          </h2>
          <div style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "2px" }}>
            Vendor: {request.vendor_name} · Category: {request.category}
          </div>
        </div>

        <div style={{
          textAlign: "right",
          fontFamily: "JetBrains Mono, monospace",
        }}>
          <div style={{ fontSize: "20px", fontWeight: 600, color: "var(--text-main)" }}>
            {formatCurrency(request.annual_cost_usd)}
          </div>
          <div style={{ fontSize: "11px", color: "var(--text-dim)" }}>
            {request.user_count ? `${request.user_count} licenses` : "Seat count undisclosed"}
          </div>
        </div>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: "16px",
        marginBottom: "20px",
        padding: "16px",
        backgroundColor: "var(--bg-surface-subtle)",
        border: "1px solid var(--border-subtle)",
        borderRadius: "4px",
      }}>
        <div>
          <div style={{ fontSize: "11px", color: "var(--text-dim)", textTransform: "uppercase" }}>
            Requester
          </div>
          <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-main)", marginTop: "2px" }}>
            {request.requester_id}
          </div>
        </div>

        <div>
          <div style={{ fontSize: "11px", color: "var(--text-dim)", textTransform: "uppercase" }}>
            Data Access Level
          </div>
          <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-main)", marginTop: "2px" }}>
            {request.data_access_level || "Unknown / Not specified"}
          </div>
        </div>

        <div>
          <div style={{ fontSize: "11px", color: "var(--text-dim)", textTransform: "uppercase" }}>
            Integrations
          </div>
          <div style={{ fontSize: "13px", fontWeight: 500, color: "var(--text-main)", marginTop: "2px" }}>
            {request.requested_integrations.length > 0
              ? request.requested_integrations.join(", ")
              : "None"}
          </div>
        </div>
      </div>

      <div>
        <div style={{
          fontSize: "11px",
          color: "var(--text-dim)",
          textTransform: "uppercase",
          marginBottom: "6px",
        }}>
          Stated Business Justification
        </div>
        <p style={{
          fontSize: "13px",
          color: "var(--text-muted)",
          backgroundColor: "var(--bg-surface-subtle)",
          padding: "12px 14px",
          border: "1px solid var(--border-subtle)",
          borderRadius: "4px",
          lineHeight: 1.6,
        }}>
          {request.business_justification || "No business purpose provided by requester."}
        </p>
      </div>
    </section>
  );
};
