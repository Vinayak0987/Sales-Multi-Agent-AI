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
    <div className="flex min-h-screen bg-[var(--bg-deep)]">
      {/* Sidebar */}
      <aside className="fixed top-0 left-0 bottom-0 z-50 w-[260px] flex flex-col bg-[var(--bg-base)] border-r border-[var(--border)]">
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-[var(--border)] mb-4">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-[var(--accent-soft)]">
            <span className="material-icons-outlined text-[var(--accent)] text-2xl">hub</span>
          </div>
          <div>
            <div className="text-[15px] font-bold tracking-[0.15em] uppercase text-[var(--text-primary)]">
              Strategic<span className="text-[var(--accent)]">Grid</span>
            </div>
            <div className="font-mono text-[10px] text-[var(--text-muted)] tracking-widest mt-0.5">
              v2.4.0 [STABLE]
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 flex flex-col gap-1 px-3">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                                    group flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200
                                    ${isActive
                    ? "bg-[var(--accent-soft)] text-[var(--accent)] font-semibold shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]"
                    : "text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]"
                  }
                                `}
              >
                <span className={`material-icons-outlined text-[20px] transition-colors ${isActive ? "text-[var(--accent)]" : "text-[var(--text-muted)] group-hover:text-[var(--text-primary)]"}`}>
                  {item.icon}
                </span>
                <span className="flex-1">{item.label}</span>
                {item.label === "Agent Monitor" && (
                  <span className="px-1.5 py-0.5 text-[9px] font-bold tracking-wider text-[var(--green)] bg-[var(--green-soft)] rounded-full">
                    ONLINE
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Footer / Storage */}
        <div className="p-4 mt-auto border-t border-[var(--border)]">
          <div className="flex justify-between items-center mb-2">
            <span className="text-[11px] font-medium text-[var(--text-muted)]">STORAGE USAGE</span>
            <span className="font-mono text-[10px] text-[var(--text-muted)]">
              <span className="text-[var(--text-primary)]">14.2 GB</span> / 20 GB
            </span>
          </div>
          <div className="h-1 w-full bg-[var(--bg-elevated)] rounded-full overflow-hidden">
            <div className="h-full w-[67%] bg-gradient-to-r from-[var(--accent)] to-[#ff6a3d] rounded-full" />
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-[260px] p-8 min-h-screen">
        {children}
      </main>
    </div>
  );
}
