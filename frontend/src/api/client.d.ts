import type { BacktestRunPayload, BacktestRunResponse, CompareExperimentsResponse, ExperimentDetail, ExperimentListItem, IngestMarketDataPayload, IngestMarketDataResponse } from "../types";
export declare function runBacktest(payload: BacktestRunPayload): Promise<BacktestRunResponse>;
export declare function ingestMarketData(payload: IngestMarketDataPayload): Promise<IngestMarketDataResponse>;
export declare function getIngestedSymbols(): Promise<string[]>;
export declare function listExperiments(): Promise<ExperimentListItem[]>;
export declare function getExperiment(id: number): Promise<ExperimentDetail>;
export declare function compareExperiments(ids: number[]): Promise<CompareExperimentsResponse>;
