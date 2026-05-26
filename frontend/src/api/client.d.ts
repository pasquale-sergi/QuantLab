import type { BacktestRunPayload, BacktestRunResponse, CompareExperimentsResponse, ExperimentDetail, ExperimentListItem } from "../types";
export declare function runBacktest(payload: BacktestRunPayload): Promise<BacktestRunResponse>;
export declare function listExperiments(): Promise<ExperimentListItem[]>;
export declare function getExperiment(id: number): Promise<ExperimentDetail>;
export declare function compareExperiments(ids: number[]): Promise<CompareExperimentsResponse>;
