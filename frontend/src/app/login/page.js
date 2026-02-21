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
        <div className="bg-paper text-ink h-screen w-full overflow-hidden flex flex-col lg:flex-row antialiased selection:bg-primary selection:text-white">
            {/* Left Pane: Brand Identity */}
            <div className="relative w-full lg:w-1/2 h-32 lg:h-full bg-ink flex flex-col justify-center items-center lg:items-start p-8 lg:p-16 overflow-hidden">
                {/* Abstract Grid Decoration (Subtle) */}
                <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: "linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)", backgroundSize: "40px 40px" }}>
                </div>

                <div className="relative z-10 flex flex-col">
                    <h1 className="font-display font-bold text-paper text-5xl lg:text-[80px] leading-[0.9] tracking-tighter uppercase">
                        Strategic<br />Grid
                    </h1>
                    <div className="mt-6 flex items-center gap-2">
                        <span className="h-px w-12 bg-primary"></span>
                        <p className="font-mono text-paper/60 text-xs uppercase tracking-widest">System v4.0.1</p>
                    </div>
                </div>

                <div className="absolute bottom-8 left-8 lg:left-16 text-paper/40 font-mono text-[10px] hidden lg:block">
                    OPERATIONAL INTELLIGENCE UNIT<br />
                    SECURE CONNECTION ESTABLISHED
                </div>
            </div>

            {/* Right Pane: Authentication Form */}
            <div className="w-full lg:w-1/2 h-full bg-paper flex flex-col justify-center items-center p-6 sm:p-12 lg:p-24 relative">
                {/* Corner Accents */}
                <div className="absolute top-0 right-0 w-8 h-8 border-l border-b border-ink"></div>
                <div className="absolute bottom-0 left-0 w-8 h-8 border-r border-t border-ink"></div>

                <div className="w-full max-w-md flex flex-col gap-8">
                    {/* Header */}
                    <div className="mb-4">
                        <h2 className="font-display font-bold text-3xl lg:text-4xl text-ink uppercase tracking-tight mb-2">Authenticate</h2>
                        <p className="font-body text-ink/60 text-sm">Enter your credentials to access the command center.</p>
                    </div>

                    {/* Form */}
                    <form className="flex flex-col gap-8" onSubmit={handleLogin}>
                        {/* Operator ID Input */}
                        <div className="relative">
                            <label className="absolute -top-2 left-4 bg-white px-2 font-mono text-xs text-ink z-10 uppercase tracking-wider" htmlFor="email">Operator ID</label>
                            <input
                                className="font-mono w-full h-[56px] bg-transparent border border-ink text-ink text-sm px-4 placeholder-ink/30 focus:outline-none focus:ring-0 focus:border-ink focus:border-2 rounded-none shadow-none"
                                id="email"
                                placeholder="user@domain.com"
                                required
                                type="email"
                                value={operatorId}
                                onChange={(e) => setOperatorId(e.target.value)}
                            />
                        </div>

                        {/* Security Key Input */}
                        <div className="relative">
                            <label className="absolute -top-2 left-4 bg-white px-2 font-mono text-xs text-ink z-10 uppercase tracking-wider" htmlFor="password">Security Key</label>
                            <input
                                className="font-mono w-full h-[56px] bg-transparent border border-ink text-ink text-sm px-4 placeholder-ink/30 focus:outline-none focus:ring-0 focus:border-ink focus:border-2 rounded-none shadow-none"
                                id="password"
                                placeholder="••••••••••••"
                                required
                                type="password"
                                value={accessKey}
                                onChange={(e) => setAccessKey(e.target.value)}
                            />
                        </div>

                        {error && (
                            <div className="p-3 bg-red-50 border border-primary text-primary text-sm font-mono">
                                {error}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            className="group relative w-full h-[56px] bg-ink text-paper font-display font-bold text-lg uppercase tracking-wide hover:bg-primary transition-colors duration-150 flex items-center justify-between px-6 disabled:opacity-50"
                            type="submit"
                            disabled={loading}
                        >
                            <span>{loading ? "INITIALIZING..." : "INITIATE SESSION"}</span>
                            <span className="material-symbols-outlined text-xl group-hover:translate-x-1 transition-transform">arrow_forward</span>
                        </button>
                    </form>

                    {/* Footer Links */}
                    <div className="flex justify-between items-center mt-4 border-t border-concrete pt-6">
                        <a className="font-mono text-xs text-ink/50 hover:text-primary transition-colors uppercase border-b border-transparent hover:border-primary pb-0.5" href="#">
                            Reset Protocol
                        </a>
                        <a className="font-mono text-xs text-ink/50 hover:text-primary transition-colors uppercase border-b border-transparent hover:border-primary pb-0.5" href="#">
                            Request Access
                        </a>
                    </div>

                    {/* Security Notice */}
                    <div className="mt-8 flex items-start gap-3 p-3 bg-concrete/50 border border-concrete">
                        <span className="material-symbols-outlined text-ink text-lg shrink-0">lock</span>
                        <p className="font-mono text-[10px] leading-relaxed text-ink/70">
                            UNAUTHORIZED ACCESS IS PROHIBITED. ALL ACTIVITIES ON THIS SYSTEM ARE LOGGED AND MONITORED FOR SECURITY PURPOSES.
                        </p>
                    </div>
                </div>
            </div>

            <style jsx global>{`
                input:-webkit-autofill,
                input:-webkit-autofill:hover, 
                input:-webkit-autofill:focus, 
                input:-webkit-autofill:active{
                    -webkit-box-shadow: 0 0 0 30px white inset !important;
                }
            `}</style>
        </div>
    );
}
