const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export async function uploadCSV(file) {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API}/leads/upload`, {
        method: "POST",
        body: formData,
    });

    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || "Upload failed");
    }

    return data;
}
