import React, { useRef } from 'react';

export function BatchFileInput({ label, fileKey, files, setFiles }) {
    const fileInputRef = useRef(null);
    const file = files[fileKey];

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFiles(prev => ({ ...prev, [fileKey]: selected }));
        }
    };

    const statusObj = file
        ? { icon: 'check_circle', text: file.name, color: 'text-data-green', border: 'border-data-green', bg: 'bg-data-green/10' }
        : { icon: 'upload', text: 'AWAITING PAYLOAD', color: 'text-ink/40', border: 'border-ink/20', bg: 'bg-paper' };

    return (
        <div
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 ${statusObj.border} ${statusObj.bg} p-4 flex items-center justify-between cursor-pointer hover:border-primary transition-colors`}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept=".csv"
            />
            <div className="flex items-center gap-4">
                <span className={`material-symbols-outlined ${statusObj.color}`}>{statusObj.icon}</span>
                <span className="font-display font-bold text-lg">{label}</span>
            </div>
            <span className={`font-mono text-sm ${statusObj.color}`}>{statusObj.text}</span>
        </div>
    );
}
