"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const router = useRouter();
    const [operatorId, setOperatorId] = useState("");
    const [accessKey, setAccessKey] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleLogin = (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        // Simulate auth — accept any credentials
        setTimeout(() => {
            setLoading(false);
            router.push("/");
        }, 1200);
    };

    return (
        <div className="login-page">
            <div className="login-bg-grid" />

            {/* Scanline effect */}
            <div className="scanline" />

            <div className="login-container animate-in">
                {/* Brand */}
                <div style={{ textAlign: "center", marginBottom: 40 }}>
                    <div style={{ display: "inline-flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                        <div style={{
                            width: 48, height: 48, borderRadius: "var(--radius-md)",
                            background: "var(--accent-soft)", border: "1px solid var(--border-accent)",
                            display: "flex", alignItems: "center", justifyContent: "center"
                        }}>
                            <span className="material-icons-outlined" style={{ fontSize: 28, color: "var(--accent)" }}>hub</span>
                        </div>
                    </div>
                    <h1 style={{ fontSize: 28, fontWeight: 700, letterSpacing: 2, textTransform: "uppercase" }}>
                        Strategic<span style={{ color: "var(--accent)" }}>Grid</span>
                    </h1>
                    <p className="mono" style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4, letterSpacing: 1 }}>
                        System v4.0.1
                    </p>
                </div>

                {/* Auth Card */}
                <div className="card" style={{ padding: 32, maxWidth: 400, margin: "0 auto" }}>
                    <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>Authenticate</h2>
                    <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 24 }}>
                        Enter your credentials to access the command center.
                    </p>

                    <form onSubmit={handleLogin}>
                        <div style={{ marginBottom: 16 }}>
                            <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 6, display: "block" }}>
                                Operator ID
                            </label>
                            <input
                                className="input"
                                type="text"
                                placeholder="Enter operator ID"
                                value={operatorId}
                                onChange={(e) => setOperatorId(e.target.value)}
                                autoFocus
                            />
                        </div>
                        <div style={{ marginBottom: 24 }}>
                            <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.8, marginBottom: 6, display: "block" }}>
                                Access Key
                            </label>
                            <input
                                className="input"
                                type="password"
                                placeholder="Enter access key"
                                value={accessKey}
                                onChange={(e) => setAccessKey(e.target.value)}
                            />
                        </div>

                        {error && (
                            <div style={{ padding: "8px 12px", background: "var(--red-soft)", borderRadius: "var(--radius-sm)", color: "var(--red)", fontSize: 12, marginBottom: 16 }}>
                                {error}
                            </div>
                        )}

                        <button type="submit" className="btn btn-primary" style={{ width: "100%", justifyContent: "center", padding: "12px 20px", fontSize: 14 }} disabled={loading}>
                            {loading ? (
                                <>
                                    <span style={{ animation: "pulse 1s infinite" }}>◈</span> Initializing Session...
                                </>
                            ) : (
                                <>
                                    <span className="material-icons-outlined" style={{ fontSize: 18 }}>lock_open</span>
                                    Initialize Session
                                </>
                            )}
                        </button>
                    </form>

                    <div style={{ display: "flex", justifyContent: "space-between", marginTop: 20 }}>
                        <a href="#" style={{ fontSize: 12, color: "var(--text-secondary)", textDecoration: "none" }}>Reset Protocol</a>
                        <a href="#" style={{ fontSize: 12, color: "var(--accent)", textDecoration: "none" }}>Request Access</a>
                    </div>
                </div>

                {/* Footer */}
                <p className="mono" style={{
                    textAlign: "center", fontSize: 10, color: "var(--text-muted)",
                    marginTop: 40, letterSpacing: 0.8, maxWidth: 360, margin: "40px auto 0"
                }}>
                    UNAUTHORIZED ACCESS IS PROHIBITED. ALL ACTIVITIES ON THIS SYSTEM ARE LOGGED AND MONITORED FOR SECURITY PURPOSES.
                </p>
            </div>

            <style jsx>{`
        .login-page {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--bg-deep);
          position: relative;
          overflow: hidden;
        }
        .login-bg-grid {
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
          background-size: 40px 40px;
        }
        .scanline {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, var(--accent-glow), transparent);
          animation: scanMove 4s ease-in-out infinite;
        }
        @keyframes scanMove {
          0%, 100% { top: 0; opacity: 0; }
          50% { top: 100%; opacity: 1; }
        }
        .login-container {
          position: relative;
          z-index: 1;
          width: 100%;
          max-width: 480px;
          padding: 40px 20px;
        }
      `}</style>
        </div>
    );
}
