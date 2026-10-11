import React, { useEffect, useState } from "react";
import { Header } from "./components/header.tsx";
import { RequestSelector } from "./components/request-selector.tsx";
import { RequestDetails } from "./components/request-details.tsx";
import { RecommendationCard } from "./components/recommendation-card.tsx";
import { EvidencePanel } from "./components/evidence-panel.tsx";
import { AuditForm } from "./components/audit-form.tsx";
import { AuditHistory } from "./components/audit-history.tsx";
import {
  ArchitectureChoice,
  HumanAuditEntry,
  ProcurementDecision,
  PurchaseRequest,
} from "./types/procurement.ts";

export const App: React.FC = () => {
  const [requests, setRequests] = useState<PurchaseRequest[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [architecture, setArchitecture] = useState<ArchitectureChoice>("single");
  const [decision, setDecision] = useState<ProcurementDecision | null>(null);
  const [auditLogs, setAuditLogs] = useState<HumanAuditEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetchRequests();
    fetchAuditLogs();
  }, []);

  const fetchRequests = async () => {
    try {
      const resp = await fetch("/api/requests");
      if (resp.ok) {
        const data: PurchaseRequest[] = await resp.json();
        setRequests(data);
        if (data.length > 0 && !selectedId) {
          setSelectedId(data[0].request_id);
        }
      }
    } catch {
      // API fallback
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const resp = await fetch("/api/audit");
      if (resp.ok) {
        const data: HumanAuditEntry[] = await resp.json();
        setAuditLogs(data);
      }
    } catch {
      // API fallback
    }
  };

  const handleRunAnalysis = async () => {
    if (!selectedId) return;
    setIsRunning(true);
    try {
      const resp = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          request_id: selectedId,
          architecture: architecture,
        }),
      });
      if (resp.ok) {
        const data: ProcurementDecision = await resp.json();
        setDecision(data);
      }
    } catch {
      // Evaluation failed
    } finally {
      setIsRunning(false);
    }
  };

  const selectedRequest = requests.find((r) => r.request_id === selectedId) || null;
  const filteredAuditLogs = auditLogs.filter((a) => a.request_id === selectedId);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <Header
        currentArch={architecture}
        onSelectArch={(arch) => {
          setArchitecture(arch);
          setDecision(null);
        }}
        isRunning={isRunning}
      />

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <RequestSelector
          requests={requests}
          selectedId={selectedId}
          onSelect={(id) => {
            setSelectedId(id);
            setDecision(null);
          }}
        />

        <main style={{
          flex: 1,
          overflowY: "auto",
          backgroundColor: "var(--bg-primary)",
        }}>
          <RequestDetails request={selectedRequest} />

          <RecommendationCard
            decision={decision}
            onExecuteAnalysis={handleRunAnalysis}
            isRunning={isRunning}
          />

          <EvidencePanel evidence={decision ? decision.evidence : []} />

          {selectedId && (
            <AuditForm
              requestId={selectedId}
              decision={decision}
              onAuditSubmitted={(entry) => setAuditLogs((prev) => [...prev, entry])}
            />
          )}

          <AuditHistory entries={filteredAuditLogs} />
        </main>
      </div>
    </div>
  );
};
