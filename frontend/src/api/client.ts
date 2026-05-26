import type {
  BacktestRunPayload,
  BacktestRunResponse,
  CompareExperimentsResponse,
  ExperimentDetail,
  ExperimentListItem,
  IngestMarketDataPayload,
  IngestMarketDataResponse,
  IngestedSymbolsResponse,
} from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
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
    } catch {
      // keep default message
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export async function runBacktest(payload: BacktestRunPayload): Promise<BacktestRunResponse> {
  return request<BacktestRunResponse>("/backtests/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function ingestMarketData(payload: IngestMarketDataPayload): Promise<IngestMarketDataResponse> {
  return request<IngestMarketDataResponse>("/market-data/ingest", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getIngestedSymbols(): Promise<string[]> {
  const response = await request<IngestedSymbolsResponse>("/market-data/symbols");
  return response.symbols;
}

export async function listExperiments(): Promise<ExperimentListItem[]> {
  return request<ExperimentListItem[]>("/backtests/experiments");
}

export async function getExperiment(id: number): Promise<ExperimentDetail> {
  return request<ExperimentDetail>(`/backtests/experiments/${id}`);
}

export async function compareExperiments(ids: number[]): Promise<CompareExperimentsResponse> {
  const idsQuery = ids.join(",");
  return request<CompareExperimentsResponse>(`/backtests/experiments/compare?ids=${idsQuery}`);
}
