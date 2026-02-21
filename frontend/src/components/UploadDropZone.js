import { useState } from "react";

export function UploadDropZone({ onSelect, file }) {
    const [dragActive, setDragActive] = useState(false);

    const handleDrag = function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = function (e) {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onSelect(e.dataTransfer.files[0]);
        }
    };

    const handleChange = function (e) {
        if (e.target.files && e.target.files[0]) {
            onSelect(e.target.files[0]);
        }
    };

    return (
        <div className="relative group">
            <div className="absolute -top-3 left-4 bg-paper px-2 z-10 border border-ink">
                <span className="font-mono text-xs font-bold uppercase tracking-wider text-ink">Phase 01: Ingestion</span>
            </div>
            <div
                className={`mt-4 h-[300px] w-full border-2 border-dashed ${dragActive ? "border-primary bg-primary/5" : "border-ink/40 bg-mute/50"
                    } relative flex flex-col items-center justify-center transition-all duration-300 hover:border-primary hover:bg-white group-hover:shadow-inner cursor-pointer`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
            >
                {/* Hatch Background Pattern Simulation */}
                <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: "repeating-linear-gradient(45deg, #0A0A0A 0, #0A0A0A 1px, transparent 0, transparent 10px)" }}></div>

                <div className="flex flex-col items-center justify-center gap-4 bg-paper/90 p-8 border border-ink shadow-sm z-10 backdrop-blur-sm">
                    <span className={`material-symbols-outlined text-5xl ${dragActive ? "text-primary" : "text-ink"}`}>upload_file</span>
                    <div className="text-center">
                        <h2 className="font-display text-2xl font-bold text-ink uppercase tracking-tight">{file ? file.name : "Drop Tactical Data (CSV)"}</h2>
                        <p className="font-mono text-xs text-ink/60 mt-2 uppercase">Max Payload: 25MB // Schema: V4.0</p>
                    </div>
                    <label className="font-mono text-xs border border-ink px-4 py-2 hover:bg-ink hover:text-paper transition-colors uppercase mt-2 cursor-pointer">
                        Select File Manually
                        <input
                            type="file"
                            className="hidden"
                            accept=".csv"
                            onChange={handleChange}
                            onClick={(e) => {
                                // Allows selecting the same file again if aborted
                                e.target.value = null;
                            }}
                        />
                    </label>
                </div>

                {/* Corner accents for 'scanner' look */}
                <div className="absolute top-0 left-0 w-4 h-4 border-l-2 border-t-2 border-ink"></div>
                <div className="absolute top-0 right-0 w-4 h-4 border-r-2 border-t-2 border-ink"></div>
                <div className="absolute bottom-0 left-0 w-4 h-4 border-l-2 border-b-2 border-ink"></div>
                <div className="absolute bottom-0 right-0 w-4 h-4 border-r-2 border-b-2 border-ink"></div>
            </div>
        </div>
    );
}
