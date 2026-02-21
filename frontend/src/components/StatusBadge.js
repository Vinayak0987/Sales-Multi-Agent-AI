export function StatusBadge({ status, analyzing = false }) {
    if (analyzing || status === "Processing") {
        return (
            <span className="inline-flex items-center px-2 py-1 border border-ink group-hover:border-paper group-hover:bg-paper group-hover:text-ink bg-white font-mono text-[10px] font-bold uppercase tracking-wide text-primary">
                Processing<span className="animate-pulse">_</span>
            </span>
        );
    }

    if (status === "Ready") {
        return (
            <span className="inline-flex items-center px-2 py-1 border border-ink group-hover:border-paper group-hover:bg-paper group-hover:text-ink bg-white font-mono text-[10px] font-bold uppercase tracking-wide">
                <span className="w-2 h-2 rounded-full bg-[#10b981] mr-2 border border-black group-hover:border-ink"></span>
                Ready
            </span>
        );
    }

    if (status === "Analysis") {
        return (
            <span className="inline-flex items-center px-2 py-1 border border-ink group-hover:border-paper group-hover:bg-paper group-hover:text-ink bg-white font-mono text-[10px] font-bold uppercase tracking-wide">
                <span className="w-2 h-2 rounded-full bg-[#eab308] mr-2 border border-black group-hover:border-ink"></span>
                Analysis
            </span>
        );
    }

    return (
        <span className="inline-flex items-center px-2 py-1 border border-ink group-hover:border-paper group-hover:bg-paper group-hover:text-ink bg-white font-mono text-[10px] font-bold uppercase tracking-wide text-ink/50 group-hover:text-ink">
            <span className="w-2 h-2 rounded-full bg-[#9ca3af] mr-2 border border-black group-hover:border-ink"></span>
            Cold
        </span>
    );
}
