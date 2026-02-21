const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function uploadBatch(files) {
    const formData = new FormData();

    if (files.agentMapping) formData.append("agent_mapping", files.agentMapping);
    if (files.crmPipeline) formData.append("crm_pipeline", files.crmPipeline);
    if (files.emailLogs) formData.append("email_logs", files.emailLogs);
    if (files.leadsData) formData.append("leads_data", files.leadsData);
    if (files.salesPipeline) formData.append("sales_pipeline", files.salesPipeline);

    const res = await fetch(`${API}/batch/upload`, {
        method: "POST",
        body: formData,
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Upload rejected by server");
    }

    return res.json();
}
