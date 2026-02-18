"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";

const NAV_ITEMS = [
    { href: "/", label: "Mission Control", icon: "dashboard", shortcut: "MC" },
    { href: "/ledger", label: "The Ledger", icon: "table_chart", shortcut: "TL" },
    { href: "/upload", label: "Upload Protocol", icon: "cloud_upload", shortcut: "UP" },
    { href: "/agents", label: "Agent Monitor", icon: "memory", shortcut: "AM" },
    { href: "/settings", label: "Settings", icon: "settings", shortcut: "ST" },
];

export default function DashboardLayout({ children }) {
    const pathname = usePathname();

    return (
        <div style={{ display: "flex", minHeight: "100vh" }}>
            {/* Sidebar */}
            <aside className="sidebar">
                {/* Logo */}
                <div className="sidebar-brand">
                    <div className="brand-icon">
                        <span className="material-icons-outlined" style={{ fontSize: 26, color: "var(--accent)" }}>hub</span>
                    </div>
                    <div>
                        <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1.5, textTransform: "uppercase" }}>
                            Strategic<span style={{ color: "var(--accent)" }}>Grid</span>
                        </div>
                        <div className="mono" style={{ fontSize: 10, color: "var(--text-muted)", letterSpacing: 1 }}>
                            v2.4.0 [STABLE]
                        </div>
                    </div>
                </div>

                {/* Nav */}
                <nav className="sidebar-nav">
                    {NAV_ITEMS.map((item) => {
                        const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
                        return (
                            <Link key={item.href} href={item.href} className={`nav-item ${isActive ? "active" : ""}`}>
                                <span className="material-icons-outlined">{item.icon}</span>
                                <span className="nav-label">{item.label}</span>
                                {item.label === "Agent Monitor" && (
                                    <span className="badge badge-green" style={{ marginLeft: "auto", fontSize: 9 }}>ONLINE</span>
                                )}
                            </Link>
                        );
                    })}
                </nav>

                {/* Storage */}
                <div className="sidebar-footer">
                    <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6, fontWeight: 500 }}>STORAGE USAGE</div>
                    <div className="storage-bar">
                        <div className="storage-fill" style={{ width: "67%" }} />
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
                        <span className="mono">14.2 GB</span> / 20 GB
                    </div>
                </div>
            </aside>

            {/* Main */}
            <main className="main-content">
                {children}
            </main>

            <style jsx>{`
        .sidebar {
          width: var(--sidebar-width);
          min-width: var(--sidebar-width);
          background: var(--bg-base);
          border-right: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          padding: 20px 12px;
          position: fixed;
          top: 0;
          left: 0;
          bottom: 0;
          z-index: 100;
        }
        .sidebar-brand {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 8px 12px 20px;
          border-bottom: 1px solid var(--border);
          margin-bottom: 16px;
        }
        .brand-icon {
          width: 40px;
          height: 40px;
          background: var(--accent-soft);
          border-radius: var(--radius-md);
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .sidebar-nav {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px 12px;
          border-radius: var(--radius-md);
          color: var(--text-secondary);
          text-decoration: none;
          font-size: 13px;
          font-weight: 500;
          transition: all 0.15s;
        }
        .nav-item:hover {
          background: var(--bg-hover);
          color: var(--text-primary);
        }
        .nav-item.active {
          background: var(--accent-soft);
          color: var(--accent);
          font-weight: 600;
        }
        .nav-item.active .material-icons-outlined {
          color: var(--accent);
        }
        .sidebar-footer {
          padding: 16px 12px;
          border-top: 1px solid var(--border);
        }
        .storage-bar {
          height: 4px;
          background: var(--bg-elevated);
          border-radius: 2px;
          overflow: hidden;
        }
        .storage-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--accent), #ff6a3d);
          border-radius: 2px;
          transition: width 0.5s;
        }
        .main-content {
          flex: 1;
          margin-left: var(--sidebar-width);
          min-height: 100vh;
          padding: 28px 32px;
          background: var(--bg-deep);
        }
      `}</style>
        </div>
    );
}
