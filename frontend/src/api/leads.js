const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function fetchLeads(page = 1, pageSize = 25, batchId = null) {
    let url = `${API}/leads?page=${page}&page_size=${pageSize}`;
    if (batchId) {
        url += `&batch_id=${batchId}`;
    }
    const res = await fetch(url);
    if (!res.ok) throw new Error("Failed to fetch leads");
    return res.json();
}
