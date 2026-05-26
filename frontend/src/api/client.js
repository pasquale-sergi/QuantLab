const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
async function request(path, init) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(init?.headers ?? {}),
        },
        ...init,
    });
    if (!response.ok) {
        let detail = `Request failed with status ${response.status}`;
        try {
            const body = await response.json();
            if (body?.detail) {
                detail = String(body.detail);
            }
        }
        catch {
            // keep default message
        }
        throw new Error(detail);
    }
    return (await response.json());
}
export async function runBacktest(payload) {
    return request("/backtests/run", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}
export async function listExperiments() {
    return request("/backtests/experiments");
}
export async function getExperiment(id) {
    return request(`/backtests/experiments/${id}`);
}
export async function compareExperiments(ids) {
    const idsQuery = ids.join(",");
    return request(`/backtests/experiments/compare?ids=${idsQuery}`);
}
