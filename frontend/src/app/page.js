"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useState, useEffect } from "react";

const API = "http://localhost:8000/api";

export default function MissionControl() {
    const [stats, setStats] = useState(null);
    const [targets, setTargets] = useState([]);
    const [activities, setActivities] = useState([]);
    const [pipeline, setPipeline] = useState([]);

    useEffect(() => {
        fetch(`${API}/dashboard/stats`).then(r => r.json()).then(setStats).catch(() => { });
        fetch(`${API}/dashboard/priority-targets`).then(r => r.json()).then(d => setTargets(d.targets || [])).catch(() => { });
        fetch(`${API}/dashboard/activity`).then(r => r.json()).then(d => setActivities(d.activities || [])).catch(() => { });
        fetch(`${API}/dashboard/pipeline`).then(r => r.json()).then(d => setPipeline(d.stages || [])).catch(() => { });
    }, []);

    const kpis = [
        { label: "Total Leads", value: stats?.total_leads?.toLocaleString() || "—", icon: "people", color: "var(--blue)" },
        { label: "Conversion Rate", value: stats ? `${stats.conversion_rate}%` : "—", icon: "trending_up", color: "var(--green)" },
        { label: "Pipeline Value", value: stats ? `$${(stats.pipeline_value / 1e6).toFixed(1)}M` : "—", icon: "attach_money", color: "var(--yellow)" },
        { label: "Active Agents", value: stats?.active_agents || "5", icon: "memory", color: "var(--purple)" },
    ];

    function timeAgo(ts) {
        if (!ts) return "";
        const diff = (Date.now() - new Date(ts).getTime()) / 1000;
        if (diff < 60) return `${Math.floor(diff)}s ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }

    return (
        <DashboardLayout>
            <div className="animate-in">
                {/* Header */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 28 }}>
                    <div>
                        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>
                            Command Center
                        </h1>
                        <p className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
                            Global Overview // {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }).toUpperCase()}
                        </p>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                        <button className="btn">
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>refresh</span>
                            Sync
                        </button>
                        <button className="btn btn-primary">
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>add</span>
                            New Target
                        </button>
                    </div>
                </div>

                {/* KPI Cards */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
                    {kpis.map((kpi, i) => (
                        <div key={i} className="card" style={{ display: "flex", alignItems: "center", gap: 16 }}>
                            <div style={{
                                width: 48, height: 48, borderRadius: "var(--radius-md)",
                                background: `${kpi.color}15`, display: "flex", alignItems: "center", justifyContent: "center"
                            }}>
                                <span className="material-icons-outlined" style={{ color: kpi.color, fontSize: 24 }}>{kpi.icon}</span>
                            </div>
                            <div>
                                <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.8 }}>
                                    {kpi.label}
                                </div>
                                <div className="mono" style={{ fontSize: 22, fontWeight: 700 }}>{kpi.value}</div>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Two-column layout */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 20 }}>
                    {/* Priority Targets */}
                    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Priority Targets</h2>
                            <a href="/ledger" className="btn" style={{ padding: "6px 14px", fontSize: 12 }}>View Full Ledger</a>
                        </div>
                        <div style={{ padding: "8px 12px" }}>
                            {targets.length === 0 ? (
                                <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 40, opacity: 0.3 }}>radar</span>
                                    <p style={{ marginTop: 8 }}>Loading targets...</p>
                                </div>
                            ) : targets.map((t, i) => (
                                <a key={i} href={`/intel/${i}`} style={{
                                    display: "flex", alignItems: "center", gap: 14, padding: "12px 10px",
                                    borderRadius: "var(--radius-md)", textDecoration: "none", color: "inherit",
                                    transition: "background 0.15s", cursor: "pointer"
                                }}
                                    onMouseEnter={e => e.currentTarget.style.background = "var(--bg-hover)"}
                                    onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                                >
                                    <div style={{
                                        width: 40, height: 40, borderRadius: "50%",
                                        background: `hsl(${(i * 60 + 200) % 360}, 40%, 25%)`,
                                        display: "flex", alignItems: "center", justifyContent: "center",
                                        fontSize: 14, fontWeight: 700, color: "#fff", flexShrink: 0
                                    }}>
                                        {(t.name || "?").charAt(0)}
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ fontWeight: 600, fontSize: 14 }}>{t.name}</div>
                                        <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{t.title} @ {t.company}</div>
                                        <div style={{ fontSize: 11, color: "var(--accent)", marginTop: 2 }}>
                                            Recent Signal: {t.signal}
                                        </div>
                                    </div>
                                    <span className="material-icons-outlined" style={{ color: "var(--text-muted)", fontSize: 18 }}>chevron_right</span>
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Agent Activity Feed */}
                    <div className="card" style={{ padding: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Agent Activity</h2>
                        </div>
                        <div style={{ flex: 1, overflowY: "auto", maxHeight: 480 }}>
                            {activities.length === 0 ? (
                                <div style={{ padding: 40, textAlign: "center", color: "var(--text-muted)" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 40, opacity: 0.3 }}>sync</span>
                                    <p style={{ marginTop: 8 }}>Loading activity...</p>
                                </div>
                            ) : activities.slice(0, 12).map((a, i) => (
                                <div key={i} style={{
                                    padding: "12px 20px", borderBottom: "1px solid var(--border-subtle)",
                                    animation: `slideIn 0.3s ease-out ${i * 0.05}s both`
                                }}>
                                    <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                                        <div style={{
                                            width: 6, height: 6, borderRadius: "50%", marginTop: 6,
                                            background: a.color || "var(--accent)", flexShrink: 0
                                        }} />
                                        <div style={{ flex: 1 }}>
                                            <p style={{ fontSize: 12, lineHeight: 1.5, color: "var(--text-primary)" }}>{a.action}</p>
                                            <span className="mono" style={{ fontSize: 10, color: "var(--text-muted)" }}>
                                                {a.agent} • {timeAgo(a.timestamp)}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Pipeline */}
                {pipeline.length > 0 && (
                    <div className="card" style={{ marginTop: 20, padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "16px 20px", borderBottom: "1px solid var(--border)" }}>
                            <h2 style={{ fontSize: 15, fontWeight: 600 }}>Sales Pipeline</h2>
                        </div>
                        <div style={{ display: "flex", padding: 20, gap: 12 }}>
                            {pipeline.map((stage, i) => (
                                <div key={i} style={{
                                    flex: 1, padding: 16, borderRadius: "var(--radius-md)",
                                    background: "var(--bg-surface)", textAlign: "center"
                                }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 600, marginBottom: 8 }}>
                                        {stage.deal_stage}
                                    </div>
                                    <div className="mono" style={{ fontSize: 20, fontWeight: 700 }}>{stage.count}</div>
                                    <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
                                        ${((stage.value || 0) / 1e6).toFixed(1)}M
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
