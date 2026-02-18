"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useState, useEffect } from "react";

const API = "http://localhost:8000/api";

const STAGES = [
    { key: "lead_research", label: "RESEARCH", icon: "search", color: "#52c41a" },
    { key: "intent_qualifier", label: "INTENT", icon: "gps_fixed", color: "#fa8c16" },
    { key: "email_strategy", label: "EMAIL STRATEGY", icon: "mail", color: "#2f54eb" },
    { key: "followup_timing", label: "TIMING", icon: "schedule", color: "#eb2f96" },
    { key: "crm_logger", label: "LOGGER", icon: "storage", color: "#722ed1" },
];

export default function AgentMonitorPage() {
    const [agents, setAgents] = useState([]);
    const [outputs, setOutputs] = useState([]);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [running, setRunning] = useState(null);
    const [runResult, setRunResult] = useState(null);

    useEffect(() => {
        fetch(`${API}/agents/status`).then(r => r.json()).then(d => setAgents(d.agents || [])).catch(() => { });
        fetch(`${API}/agents/outputs`).then(r => r.json()).then(d => setOutputs(d.outputs || [])).catch(() => { });
    }, []);

    const runAgent = async (agentId) => {
        setRunning(agentId);
        setRunResult(null);
        try {
            const res = await fetch(`${API}/agents/run/${agentId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({}),
            });
            const data = await res.json();
            setRunResult(data);
            // Refresh status
            fetch(`${API}/agents/status`).then(r => r.json()).then(d => setAgents(d.agents || [])).catch(() => { });
        } catch (err) {
            setRunResult({ error: "Connection failed" });
        }
        setRunning(null);
    };

    const getStageStatus = (key) => {
        const agent = agents.find(a => a.id === key);
        if (running === key) return "running";
        return agent?.status || "idle";
    };

    const statusBadge = (status) => {
        switch (status) {
            case "completed": return <span className="badge badge-green">COMPLETE</span>;
            case "running": return <span className="badge badge-yellow" style={{ animation: "pulse 1.5s infinite" }}>RUNNING</span>;
            case "error": return <span className="badge badge-red">ERROR</span>;
            default: return <span className="badge" style={{ background: "var(--bg-elevated)", color: "var(--text-muted)" }}>IDLE</span>;
        }
    };

    return (
        <DashboardLayout>
            <div className="animate-in">
                <div style={{ marginBottom: 28 }}>
                    <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Agent Monitor</h1>
                    <p className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
                        MULTI-AGENT PIPELINE STATUS // 5 AGENTS ONLINE
                    </p>
                </div>

                {/* Pipeline Visualization */}
                <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 24 }}>
                    <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <h2 style={{ fontSize: 15, fontWeight: 600 }}>Processing Pipeline</h2>
                        <span className="badge badge-green">SYSTEM ONLINE</span>
                    </div>
                    <div style={{ padding: 24, display: "flex", alignItems: "center", justifyContent: "center", gap: 0 }}>
                        {STAGES.map((stage, i) => (
                            <div key={stage.key} style={{ display: "flex", alignItems: "center" }}>
                                {/* Stage card */}
                                <div
                                    onClick={() => setSelectedAgent(stage.key)}
                                    style={{
                                        padding: "20px 24px",
                                        borderRadius: "var(--radius-lg)",
                                        background: selectedAgent === stage.key ? `${stage.color}18` : "var(--bg-surface)",
                                        border: `1px solid ${selectedAgent === stage.key ? stage.color + "40" : "var(--border)"}`,
                                        textAlign: "center",
                                        cursor: "pointer",
                                        transition: "all 0.2s",
                                        minWidth: 140,
                                    }}
                                >
                                    <div style={{
                                        width: 48, height: 48, borderRadius: "50%",
                                        background: `${stage.color}20`, margin: "0 auto 12px",
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                    }}>
                                        <span className="material-icons-outlined" style={{ color: stage.color, fontSize: 24 }}>{stage.icon}</span>
                                    </div>
                                    <div className="mono" style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, marginBottom: 8 }}>
                                        {stage.label}
                                    </div>
                                    {statusBadge(getStageStatus(stage.key))}
                                </div>
                                {/* Arrow connector */}
                                {i < STAGES.length - 1 && (
                                    <div style={{ padding: "0 8px", color: "var(--text-muted)" }}>
                                        <span className="material-icons-outlined" style={{ fontSize: 20 }}>arrow_forward</span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
                    {/* Agent Detail */}
                    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Agent Details</h2>
                        </div>
                        <div style={{ padding: 20 }}>
                            {agents.length === 0 ? (
                                <div style={{ textAlign: "center", padding: 30, color: "var(--text-muted)" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 40, opacity: 0.3 }}>smart_toy</span>
                                    <p style={{ marginTop: 8 }}>Select an agent from the pipeline above</p>
                                </div>
                            ) : (
                                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                    {agents.map((agent) => {
                                        const stageInfo = STAGES.find(s => s.key === agent.id);
                                        return (
                                            <div
                                                key={agent.id}
                                                onClick={() => setSelectedAgent(agent.id)}
                                                style={{
                                                    padding: "14px 16px",
                                                    borderRadius: "var(--radius-md)",
                                                    background: selectedAgent === agent.id ? "var(--bg-hover)" : "transparent",
                                                    border: "1px solid var(--border-subtle)",
                                                    cursor: "pointer",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    gap: 12,
                                                    transition: "all 0.15s",
                                                }}
                                            >
                                                <div style={{
                                                    width: 36, height: 36, borderRadius: "var(--radius-sm)",
                                                    background: `${stageInfo?.color || "#666"}20`,
                                                    display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                                                }}>
                                                    <span className="material-icons-outlined" style={{ color: stageInfo?.color, fontSize: 18 }}>{stageInfo?.icon}</span>
                                                </div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: 600, fontSize: 13 }}>{agent.name}</div>
                                                    <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>{agent.description}</div>
                                                </div>
                                                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                                                    {statusBadge(running === agent.id ? "running" : agent.status)}
                                                    <button
                                                        className="btn"
                                                        style={{ padding: "4px 10px", fontSize: 11 }}
                                                        onClick={(e) => { e.stopPropagation(); runAgent(agent.id); }}
                                                        disabled={running === agent.id}
                                                    >
                                                        {running === agent.id ? "..." : "Run"}
                                                    </button>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Outputs */}
                    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Agent Outputs</h2>
                        </div>
                        <div style={{ padding: 20 }}>
                            {outputs.length === 0 ? (
                                <div style={{ textAlign: "center", padding: 30, color: "var(--text-muted)" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 40, opacity: 0.3 }}>inventory_2</span>
                                    <p style={{ marginTop: 8 }}>No outputs available</p>
                                </div>
                            ) : outputs.map((out, i) => (
                                <div key={i} style={{
                                    padding: "12px 14px", borderRadius: "var(--radius-md)",
                                    border: "1px solid var(--border-subtle)", marginBottom: 8,
                                    transition: "all 0.15s",
                                }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                                        <span className="material-icons-outlined" style={{ fontSize: 18, color: "var(--green)" }}>check_circle</span>
                                        <span style={{ fontWeight: 600, fontSize: 13 }}>{out.agent.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}</span>
                                        <span className="mono" style={{ fontSize: 10, color: "var(--text-muted)", marginLeft: "auto" }}>
                                            {(out.size_bytes / 1024).toFixed(1)} KB
                                        </span>
                                    </div>
                                    <div className="mono" style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5, overflow: "hidden", maxHeight: 42 }}>
                                        {out.preview}
                                    </div>
                                </div>
                            ))}

                            {/* Run Result */}
                            {runResult && (
                                <div className="card" style={{ marginTop: 12, background: runResult.error ? "var(--red-soft)" : "var(--green-soft)", padding: 14 }}>
                                    <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4, color: runResult.error ? "var(--red)" : "var(--green)" }}>
                                        {runResult.error ? "Error" : `Agent: ${runResult.agent_id}`}
                                    </div>
                                    <div className="mono" style={{ fontSize: 11, color: "var(--text-secondary)", maxHeight: 80, overflow: "auto" }}>
                                        {runResult.error || JSON.stringify(runResult.result, null, 2)?.slice(0, 300)}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
