"use client";
import DashboardLayout from "@/components/DashboardLayout";
import { useState, useEffect } from "react";

const API = "http://localhost:8000/api";

export default function LedgerPage() {
    const [leads, setLeads] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [search, setSearch] = useState("");
    const [searchInput, setSearchInput] = useState("");
    const [filters, setFilters] = useState({ regions: [], sources: [] });
    const [regionFilter, setRegionFilter] = useState("");
    const [sourceFilter, setSourceFilter] = useState("");
    const [loading, setLoading] = useState(true);

    const fetchLeads = () => {
        setLoading(true);
        const params = new URLSearchParams({ page, page_size: 20 });
        if (search) params.set("search", search);
        if (regionFilter) params.set("region", regionFilter);
        if (sourceFilter) params.set("lead_source", sourceFilter);
        fetch(`${API}/leads?${params}`)
            .then(r => r.json())
            .then(d => {
                setLeads(d.leads || []);
                setTotal(d.total || 0);
                setTotalPages(d.total_pages || 1);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        fetch(`${API}/leads/filters`).then(r => r.json()).then(setFilters).catch(() => { });
    }, []);

    useEffect(() => { fetchLeads(); }, [page, search, regionFilter, sourceFilter]);

    const handleSearch = (e) => {
        e.preventDefault();
        setPage(1);
        setSearch(searchInput);
    };

    return (
        <DashboardLayout>
            <div className="animate-in">
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
                    <div>
                        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>The Ledger</h1>
                        <p className="mono" style={{ color: "var(--text-muted)", fontSize: 12 }}>
                            {total.toLocaleString()} TARGETS IN DATABASE
                        </p>
                    </div>
                    <div style={{ display: "flex", gap: 8 }}>
                        <button className="btn" onClick={fetchLeads}>
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>refresh</span>
                            Refresh
                        </button>
                        <a href="/upload" className="btn btn-primary">
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>cloud_upload</span>
                            Upload
                        </a>
                    </div>
                </div>

                {/* Filters */}
                <div className="card" style={{ display: "flex", gap: 12, marginBottom: 20, padding: 14, alignItems: "center" }}>
                    <form onSubmit={handleSearch} style={{ flex: 1, display: "flex", gap: 8 }}>
                        <div style={{ position: "relative", flex: 1 }}>
                            <span className="material-icons-outlined" style={{ position: "absolute", left: 12, top: 10, fontSize: 18, color: "var(--text-muted)" }}>search</span>
                            <input
                                className="input"
                                style={{ paddingLeft: 38 }}
                                placeholder="Search leads..."
                                value={searchInput}
                                onChange={(e) => setSearchInput(e.target.value)}
                            />
                        </div>
                        <button type="submit" className="btn" style={{ padding: "10px 16px" }}>Search</button>
                    </form>
                    <select className="input" style={{ width: 160 }} value={regionFilter} onChange={e => { setRegionFilter(e.target.value); setPage(1); }}>
                        <option value="">All Regions</option>
                        {filters.regions?.slice(0, 20).map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                    <select className="input" style={{ width: 160 }} value={sourceFilter} onChange={e => { setSourceFilter(e.target.value); setPage(1); }}>
                        <option value="">All Sources</option>
                        {filters.sources?.slice(0, 20).map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                </div>

                {/* Table */}
                <div className="table-wrapper">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Title</th>
                                <th>Company</th>
                                <th>Region</th>
                                <th>Source</th>
                                <th>Visits</th>
                                <th>Status</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan={8} style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>
                                    <span style={{ animation: "pulse 1s infinite" }}>◈</span> Loading targets...
                                </td></tr>
                            ) : leads.length === 0 ? (
                                <tr><td colSpan={8} style={{ textAlign: "center", padding: 40, color: "var(--text-muted)" }}>No leads found</td></tr>
                            ) : leads.map((lead, i) => (
                                <tr key={i} style={{ cursor: "pointer" }} onClick={() => window.location.href = `/intel/${i + (page - 1) * 20}`}>
                                    <td>
                                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                                            <div style={{
                                                width: 32, height: 32, borderRadius: "50%",
                                                background: `hsl(${((i * 37 + 100) % 360)}, 35%, 30%)`,
                                                display: "flex", alignItems: "center", justifyContent: "center",
                                                fontSize: 12, fontWeight: 700, color: "#fff", flexShrink: 0
                                            }}>
                                                {(lead.name || "?").charAt(0)}
                                            </div>
                                            <span style={{ fontWeight: 500 }}>{lead.name || "—"}</span>
                                        </div>
                                    </td>
                                    <td style={{ color: "var(--text-secondary)" }}>{lead.title || "—"}</td>
                                    <td>{lead.company || "—"}</td>
                                    <td><span className="badge badge-blue">{lead.region || "—"}</span></td>
                                    <td style={{ fontSize: 12, color: "var(--text-secondary)" }}>{lead.lead_source || "—"}</td>
                                    <td className="mono" style={{ fontSize: 12 }}>{lead.visits ?? "—"}</td>
                                    <td>
                                        {lead.converted ? (
                                            <span className="badge badge-green">Converted</span>
                                        ) : (
                                            <span className="badge badge-yellow">Active</span>
                                        )}
                                    </td>
                                    <td>
                                        <span className="material-icons-outlined" style={{ fontSize: 16, color: "var(--text-muted)" }}>chevron_right</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
                    <span className="mono" style={{ fontSize: 12, color: "var(--text-muted)" }}>
                        Page {page} of {totalPages} ({total.toLocaleString()} total)
                    </span>
                    <div style={{ display: "flex", gap: 6 }}>
                        <button className="btn" style={{ padding: "6px 12px" }} disabled={page <= 1} onClick={() => setPage(p => p - 1)}>
                            <span className="material-icons-outlined" style={{ fontSize: 16 }}>chevron_left</span> Prev
                        </button>
                        <button className="btn" style={{ padding: "6px 12px" }} disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>
                            Next <span className="material-icons-outlined" style={{ fontSize: 16 }}>chevron_right</span>
                        </button>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
