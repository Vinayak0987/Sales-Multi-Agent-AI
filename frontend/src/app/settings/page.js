"use client";
import DashboardLayout from "@/components/DashboardLayout";

export default function SettingsPage() {
    return (
        <DashboardLayout>
            <div className="animate-in">
                <div style={{ marginBottom: 28 }}>
                    <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Settings</h1>
                    <p className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
                        SYSTEM CONFIGURATION // V2.4.0
                    </p>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, maxWidth: 800 }}>
                    {/* API Config */}
                    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600 }}>
                            API Configuration
                        </div>
                        <div style={{ padding: 20 }}>
                            <div style={{ marginBottom: 16 }}>
                                <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 6, display: "block" }}>
                                    Backend URL
                                </label>
                                <input className="input" defaultValue="http://localhost:8000" readOnly />
                            </div>
                            <div>
                                <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 6, display: "block" }}>
                                    Gemini API Key
                                </label>
                                <input className="input" type="password" defaultValue="••••••••••••" readOnly />
                            </div>
                        </div>
                    </div>

                    {/* System Info */}
                    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600 }}>
                            System Info
                        </div>
                        <div style={{ padding: "4px 0" }}>
                            {[
                                { label: "Version", value: "v2.4.0 [STABLE]" },
                                { label: "Agents", value: "5 Online" },
                                { label: "LLM", value: "Gemini" },
                                { label: "Framework", value: "LangGraph" },
                                { label: "Frontend", value: "Next.js 15" },
                            ].map((item, i) => (
                                <div key={i} style={{ display: "flex", justifyContent: "space-between", padding: "10px 20px", borderBottom: "1px solid var(--border-subtle)" }}>
                                    <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{item.label}</span>
                                    <span className="mono" style={{ fontSize: 12 }}>{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Data Sources */}
                    <div className="card" style={{ padding: 0, overflow: "hidden", gridColumn: "1 / -1" }}>
                        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600 }}>
                            Data Sources
                        </div>
                        <div style={{ padding: "4px 0" }}>
                            {[
                                { file: "Leads_Data.csv", desc: "Primary lead database", status: "active" },
                                { file: "Sales_Pipeline.csv", desc: "Sales pipeline deals", status: "active" },
                                { file: "Email_Logs.csv", desc: "Historical email interactions", status: "active" },
                                { file: "CRM_Pipeline.csv", desc: "CRM pipeline data", status: "active" },
                                { file: "Agent_Mapping.csv", desc: "Sales agent assignments", status: "active" },
                            ].map((ds, i) => (
                                <div key={i} style={{ display: "flex", alignItems: "center", padding: "12px 20px", borderBottom: "1px solid var(--border-subtle)", gap: 12 }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 18, color: "var(--green)" }}>check_circle</span>
                                    <div style={{ flex: 1 }}>
                                        <div className="mono" style={{ fontSize: 13, fontWeight: 500 }}>{ds.file}</div>
                                        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{ds.desc}</div>
                                    </div>
                                    <span className="badge badge-green">LOADED</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
