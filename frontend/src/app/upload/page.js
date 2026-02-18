"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useState, useRef } from "react";

const API = "http://localhost:8000/api";

export default function UploadPage() {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState("");
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
        else if (e.type === "dragleave") setDragActive(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        const dropped = e.dataTransfer?.files?.[0];
        if (dropped && dropped.name.endsWith(".csv")) {
            setFile(dropped);
            setError("");
        } else {
            setError("Only CSV files are accepted.");
        }
    };

    const handleSelect = (e) => {
        const selected = e.target.files?.[0];
        if (selected) {
            setFile(selected);
            setError("");
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        setError("");
        setResult(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API}/leads/upload`, { method: "POST", body: formData });
            const data = await res.json();
            if (res.ok) {
                setResult(data);
            } else {
                setError(data.detail || "Upload failed");
            }
        } catch (err) {
            setError("Connection failed. Is the backend running?");
        }
        setUploading(false);
    };

    return (
        <DashboardLayout>
            <div className="animate-in">
                <div style={{ marginBottom: 28 }}>
                    <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>Upload Protocol</h1>
                    <p className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
                        SECURE DATA INGESTION INTERFACE // V.2.4
                    </p>
                </div>

                <div style={{ maxWidth: 680, margin: "0 auto" }}>
                    {/* Drop Zone */}
                    <div
                        className="card"
                        onDragEnter={handleDrag}
                        onDragOver={handleDrag}
                        onDragLeave={handleDrag}
                        onDrop={handleDrop}
                        onClick={() => inputRef.current?.click()}
                        style={{
                            textAlign: "center",
                            padding: "60px 40px",
                            cursor: "pointer",
                            border: dragActive ? "2px dashed var(--accent)" : "2px dashed var(--border)",
                            background: dragActive ? "var(--accent-soft)" : "var(--bg-card)",
                            transition: "all 0.2s",
                        }}
                    >
                        <input ref={inputRef} type="file" accept=".csv" onChange={handleSelect} hidden />
                        <span className="material-icons-outlined" style={{ fontSize: 56, color: dragActive ? "var(--accent)" : "var(--text-muted)", marginBottom: 16 }}>
                            cloud_upload
                        </span>
                        <h3 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                            Drop Tactical Data (CSV)
                        </h3>
                        <p style={{ color: "var(--text-secondary)", fontSize: 13 }}>
                            Drag and drop your CSV file here, or click to browse
                        </p>
                        <div className="mono" style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 12 }}>
                            Max Payload: 25MB // Schema: V4.0
                        </div>
                    </div>

                    {/* Selected file */}
                    {file && !result && (
                        <div className="card" style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 14 }}>
                            <div style={{
                                width: 44, height: 44, borderRadius: "var(--radius-md)",
                                background: "var(--green-soft)", display: "flex", alignItems: "center", justifyContent: "center"
                            }}>
                                <span className="material-icons-outlined" style={{ color: "var(--green)", fontSize: 22 }}>description</span>
                            </div>
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, fontSize: 14 }}>{file.name}</div>
                                <div className="mono" style={{ fontSize: 11, color: "var(--text-muted)" }}>
                                    {(file.size / 1024).toFixed(1)} KB
                                </div>
                            </div>
                            <button className="btn" onClick={() => { setFile(null); setResult(null); }} style={{ padding: "6px 12px" }}>
                                <span className="material-icons-outlined" style={{ fontSize: 16 }}>close</span>
                            </button>
                            <button className="btn btn-primary" onClick={handleUpload} disabled={uploading} style={{ padding: "10px 20px" }}>
                                {uploading ? (
                                    <><span style={{ animation: "pulse 1s infinite" }}>◈</span> Processing...</>
                                ) : (
                                    <><span className="material-icons-outlined" style={{ fontSize: 16 }}>upload</span> Upload</>
                                )}
                            </button>
                        </div>
                    )}

                    {/* Error */}
                    {error && (
                        <div className="card" style={{ marginTop: 16, background: "var(--red-soft)", borderColor: "var(--red)" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 10, color: "var(--red)" }}>
                                <span className="material-icons-outlined" style={{ fontSize: 20 }}>error</span>
                                <span style={{ fontSize: 13 }}>{error}</span>
                            </div>
                        </div>
                    )}

                    {/* Result */}
                    {result && (
                        <div className="card" style={{ marginTop: 16, borderColor: "var(--green)", background: "var(--green-soft)" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                                <span className="material-icons-outlined" style={{ color: "var(--green)", fontSize: 22 }}>check_circle</span>
                                <span style={{ fontWeight: 600, color: "var(--green)", fontSize: 15 }}>Upload Successful</span>
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                                <div style={{ padding: 12, background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-md)" }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase" }}>File</div>
                                    <div className="mono" style={{ fontSize: 14, marginTop: 4 }}>{result.filename}</div>
                                </div>
                                <div style={{ padding: 12, background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-md)" }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase" }}>Rows Ingested</div>
                                    <div className="mono" style={{ fontSize: 14, marginTop: 4 }}>{result.rows?.toLocaleString()}</div>
                                </div>
                            </div>
                            {result.columns && (
                                <div style={{ marginTop: 12, padding: 12, background: "rgba(0,0,0,0.2)", borderRadius: "var(--radius-md)" }}>
                                    <div style={{ fontSize: 11, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", marginBottom: 6 }}>Detected Schema</div>
                                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                                        {result.columns.map((col, i) => (
                                            <span key={i} className="badge badge-blue">{col}</span>
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div style={{ marginTop: 16, display: "flex", gap: 8 }}>
                                <a href="/ledger" className="btn btn-primary" style={{ flex: 1, justifyContent: "center" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 16 }}>table_chart</span> View in Ledger
                                </a>
                                <button className="btn" onClick={() => { setFile(null); setResult(null); }} style={{ flex: 1, justifyContent: "center" }}>
                                    <span className="material-icons-outlined" style={{ fontSize: 16 }}>cloud_upload</span> Upload Another
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Specs */}
                    <div className="card" style={{ marginTop: 24, padding: 0, overflow: "hidden" }}>
                        <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>
                            Ingestion Specifications
                        </div>
                        <div style={{ padding: "16px 20px", fontSize: 13, color: "var(--text-secondary)" }}>
                            <div style={{ display: "grid", gridTemplateColumns: "140px 1fr", gap: "8px 16px" }}>
                                <span style={{ color: "var(--text-muted)" }}>Format</span><span>CSV (Comma Separated Values)</span>
                                <span style={{ color: "var(--text-muted)" }}>Max Size</span><span>25 MB</span>
                                <span style={{ color: "var(--text-muted)" }}>Encoding</span><span>UTF-8</span>
                                <span style={{ color: "var(--text-muted)" }}>Expected</span><span>name, title, company, region, lead_source, visits, converted</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
