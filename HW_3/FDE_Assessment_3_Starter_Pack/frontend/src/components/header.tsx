import React from "react";
import { ArchitectureChoice } from "../types/procurement.ts";

interface HeaderProps {
  currentArch: ArchitectureChoice;
  onSelectArch: (arch: ArchitectureChoice) => void;
  isRunning: boolean;
}

export const Header: React.FC<HeaderProps> = ({ currentArch, onSelectArch, isRunning }) => {
  return (
    <header style={{
      borderBottom: "1px solid var(--border-subtle)",
      padding: "16px 24px",
      backgroundColor: "var(--bg-surface)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span style={{
          fontSize: "12px",
          fontWeight: 600,
          letterSpacing: "0.08em",
          color: "var(--text-dim)",
          textTransform: "uppercase",
          fontFamily: "JetBrains Mono, monospace",
        }}>
          PROCUREMENT
        </span>
        <span style={{ color: "var(--border-active)" }}>/</span>
        <h1 style={{ fontSize: "15px", fontWeight: 600, color: "var(--text-main)" }}>
          Procurement Request Copilot
        </h1>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontSize: "12px", color: "var(--text-dim)", marginRight: "4px" }}>
          Engine:
        </span>
        <button
          onClick={() => onSelectArch("single")}
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            fontWeight: 500,
            borderRadius: "4px",
            backgroundColor: currentArch === "single" ? "var(--bg-surface-active)" : "transparent",
            color: currentArch === "single" ? "var(--text-main)" : "var(--text-muted)",
            border: currentArch === "single" ? "1px solid var(--border-active)" : "1px solid transparent",
          }}
        >
          Architecture A (Single)
        </button>
        <button
          onClick={() => onSelectArch("staged")}
          style={{
            padding: "6px 12px",
            fontSize: "12px",
            fontWeight: 500,
            borderRadius: "4px",
            backgroundColor: currentArch === "staged" ? "var(--bg-surface-active)" : "transparent",
            color: currentArch === "staged" ? "var(--text-main)" : "var(--text-muted)",
            border: currentArch === "staged" ? "1px solid var(--border-active)" : "1px solid transparent",
          }}
        >
          Architecture B (Staged)
        </button>
        {isRunning && (
          <span style={{
            fontSize: "12px",
            color: "var(--text-dim)",
            fontFamily: "JetBrains Mono, monospace",
            marginLeft: "8px",
          }}>
            [Evaluating...]
          </span>
        )}
      </div>
    </header>
  );
};
