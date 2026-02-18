"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useState, useEffect, use } from "react";

const API = "http://localhost:8000/api";

export default function IntelPage({ params }) {
    const resolvedParams = use(params);
    const id = resolvedParams.id;
    const [lead, setLead] = useState(null);
    const [loading, setLoading] = useState(true);
    const [agentResults, setAgentResults] = useState({});
    const [runningAgent, setRunningAgent] = useState(null);

    useEffect(() => {
        fetch(`${API}/leads/${id}`)
            .then(r => r.json())
            .then(d => { setLead(d); setLoading(false); })
            .catch(() => setLoading(false));
    }, [id]);

    const runAgent = async (agentId) => {
        setRunningAgent(agentId);
        try {
            const res = await fetch(`${API}/agents/run/${agentId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ lead_id: id }),
            });
            const data = await res.json();
            setAgentResults(prev => ({ ...prev, [agentId]: data }));
        } catch (err) {
            setAgentResults(prev => ({ ...prev, [agentId]: { error: "Connection failed" } }));
        }
        setRunningAgent(null);
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div style={{ textAlign: "center", padding: 80, color: "var(--text-muted)" }}>
                    <span style={{ animation: "pulse 1s infinite", fontSize: 24 }}>◈</span>
                    <p style={{ marginTop: 12 }}>Loading Intelligence Report...</p>
                </div>
            </DashboardLayout>
        );
    }

    if (!lead) {
        return (
            <DashboardLayout>
                <div style={{ textAlign: "center", padding: 80, color: "var(--text-muted)" }}>
                    <span className="material-icons-outlined" style={{ fontSize: 48, opacity: 0.3 }}>person_off</span>
                    <p style={{ marginTop: 12 }}>Target not found</p>
                    <a href="/ledger" className="btn" style={{ marginTop: 16 }}>Return to Ledger</a>
                </div>
            </DashboardLayout>
        );
    }

    const agents = [
        { id: "lead_research", label: "Lead Research", icon: "search", color: "#52c41a", desc: "Behavioral pattern analysis" },
        { id: "intent_qualifier", label: "Intent Qualifier", icon: "gps_fixed", color: "#fa8c16", desc: "Engagement scoring" },
        { id: "email_strategy", label: "Email Strategy", icon: "mail", color: "#2f54eb", desc: "Personalized outreach" },
        { id: "followup_timing", label: "Follow-up Timing", icon: "schedule", color: "#eb2f96", desc: "Optimal timing" },
    ];

    // Build detail fields from available lead data
    const fields = [
        { label: "Name", value: lead.name },
        { label: "Title", value: lead.title },
        { label: "Company", value: lead.company },
        { label: "Region", value: lead.region },
        { label: "Source", value: lead.lead_source },
        { label: "Visits", value: lead.visits },
        { label: "Time on Site", value: lead.time_on_site ? `${Number(lead.time_on_site).toFixed(0)}s` : undefined },
        { label: "Pages/Visit", value: lead.pages_per_visit ? Number(lead.pages_per_visit).toFixed(1) : undefined },
        { label: "Converted", value: lead.converted !== undefined ? (lead.converted ? "Yes" : "No") : undefined },
    ].filter(f => f.value !== undefined && f.value !== null && f.value !== "");

    return (
        <DashboardLayout>
            <div className="animate-in">
                {/* Breadcrumb */}
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20, fontSize: 13, color: "var(--text-muted)" }}>
                    <a href="/ledger" style={{ color: "var(--text-secondary)", textDecoration: "none" }}>The Ledger</a>
                    <span className="material-icons-outlined" style={{ fontSize: 14 }}>chevron_right</span>
                    <span style={{ color: "var(--accent)" }}>Intelligence Report</span>
                </div>

                {/* Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 28 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                        <div style={{
                            width: 56, height: 56, borderRadius: "50%",
                            background: `hsl(${(id * 37 + 100) % 360}, 35%, 30%)`,
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: 22, fontWeight: 700, color: "#fff"
                        }}>
                            {(lead.name || "?").charAt(0)}
                        </div>
                        <div>
                            <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 2 }}>{lead.name || `Target #${id}`}</h1>
                            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
                                {lead.title} {lead.company ? `@ ${lead.company}` : ""}
                            </p>
                        </div>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                        <button className="btn">
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>bookmark_border</span>
                            Watch
                        </button>
                        <button className="btn btn-primary" onClick={() => runAgent("lead_research")}>
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>play_arrow</span>
                            Run Full Analysis
                        </button>
                    </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 20 }}>
                    {/* Left: Lead Details */}
                    <div>
                        <div className="card" style={{ padding: 0, overflow: "hidden", marginBottom: 16 }}>
                            <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600 }}>
                                Target Profile
                            </div>
                            <div style={{ padding: "4px 0" }}>
                                {fields.map((f, i) => (
                                    <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "10px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
                                        <span style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.5 }}>{f.label}</span>
                                        <span style={{ fontSize: 13, fontWeight: 500 }}>{f.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* CRM Timeline */}
                        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                            <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600 }}>
                                Event Timeline
                            </div>
                            <div style={{ padding: 20 }}>
                                {[
                                    { icon: "person_add", text: "Lead added to system", time: "2 days ago", color: "var(--blue)" },
                                    { icon: "search", text: "Research initiated", time: "1 day ago", color: "#52c41a" },
                                    { icon: "gps_fixed", text: "Intent scored", time: "12 hours ago", color: "#fa8c16" },
                                ].map((ev, i) => (
                                    <div key={i} style={{ display: "flex", gap: 12, marginBottom: 16, position: "relative" }}>
                                        {i < 2 && <div style={{ position: "absolute", left: 15, top: 28, bottom: -12, width: 1, background: "var(--border)" }} />}
                                        <div style={{
                                            width: 30, height: 30, borderRadius: "50%", background: `${ev.color}20`,
                                            display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0
                                        }}>
                                            <span className="material-icons-outlined" style={{ fontSize: 14, color: ev.color }}>{ev.icon}</span>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: 13, fontWeight: 500 }}>{ev.text}</div>
                                            <div className="mono" style={{ fontSize: 10, color: "var(--text-muted)" }}>{ev.time}</div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Right: Agent Panels */}
                    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                        {agents.map((agent) => (
                            <div key={agent.id} className="card" style={{ padding: 0, overflow: "hidden" }}>
                                <div style={{
                                    padding: "14px 20px", borderBottom: "1px solid var(--border)",
                                    display: "flex", justifyContent: "space-between", alignItems: "center"
                                }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                        <div style={{
                                            width: 32, height: 32, borderRadius: "var(--radius-sm)",
                                            background: `${agent.color}20`, display: "flex", alignItems: "center", justifyContent: "center"
                                        }}>
                                            <span className="material-icons-outlined" style={{ color: agent.color, fontSize: 18 }}>{agent.icon}</span>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: 14, fontWeight: 600 }}>{agent.label}</div>
                                            <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{agent.desc}</div>
                                        </div>
                                    </div>
                                    <button
                                        className="btn"
                                        style={{ padding: "6px 14px", fontSize: 12 }}
                                        onClick={() => runAgent(agent.id)}
                                        disabled={runningAgent === agent.id}
                                    >
                                        {runningAgent === agent.id ? (
                                            <><span style={{ animation: "pulse 1s infinite" }}>◈</span> Running...</>
                                        ) : (
                                            <><span className="material-icons-outlined" style={{ fontSize: 14 }}>play_arrow</span> Run</>
                                        )}
                                    </button>
                                </div>
                                <div style={{ padding: 20 }}>
                                    {agentResults[agent.id] ? (
                                        agentResults[agent.id].error ? (
                                            <div style={{ color: "var(--red)", fontSize: 13 }}>{agentResults[agent.id].error}</div>
                                        ) : (
                                            <div>
                                                <div className="badge badge-green" style={{ marginBottom: 10 }}>ANALYSIS COMPLETE</div>
                                                <pre className="mono" style={{
                                                    fontSize: 11, color: "var(--text-secondary)",
                                                    background: "var(--bg-base)", padding: 14, borderRadius: "var(--radius-md)",
                                                    maxHeight: 200, overflow: "auto", whiteSpace: "pre-wrap", wordBreak: "break-word"
                                                }}>
                                                    {JSON.stringify(agentResults[agent.id].result, null, 2)?.slice(0, 1000) || "No data"}
                                                </pre>
                                            </div>
                                        )
                                    ) : (
                                        <div style={{ textAlign: "center", padding: 20, color: "var(--text-muted)" }}>
                                            <span className="material-icons-outlined" style={{ fontSize: 32, opacity: 0.3 }}>smart_toy</span>
                                            <p style={{ fontSize: 12, marginTop: 8 }}>Click "Run" to execute this agent</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
