export type BacktestRunPayload = {
  symbol: string;
  start_date: string;
  end_date: string;
  strategy: "moving_average_crossover";
  parameters: {
    short_window: number;
    long_window: number;
  };
  initial_cash: number;
  transaction_cost_bps: number;
};

export type BacktestMetrics = {
  total_return: number | null;
  annualized_return: number | null;
  volatility: number | null;
  annualized_volatility: number | null;
  sharpe_ratio: number | null;
  max_drawdown: number | null;
  historical_var_95: number | null;
  expected_shortfall_95: number | null;
  number_of_trades: number;
  buy_trades: number;
  sell_trades: number;
  time_in_market_pct: number;
  best_day: number | null;
  worst_day: number | null;
  average_daily_return: number | null;
};

export type Trade = {
  date: string;
  symbol: string;
  side: string;
  price: number;
  shares: number;
  gross_value: number;
  transaction_cost: number;
  cash_after_trade: number;
};

export type EquityPoint = {
  date: string;
  cash: number;
  shares: number;
  close_price: number;
  position_value: number;
  total_equity: number;
  daily_return: number | null;
};

export type BacktestRunResponse = {
  experiment_id: number;
  symbol: string;
  strategy: string;
  parameters: { short_window: number; long_window: number };
  start_date: string;
  end_date: string;
  transaction_cost_bps: number;
  initial_cash: number;
  final_equity: number;
  metrics: BacktestMetrics;
  trades: Trade[];
  equity_curve: EquityPoint[];
};

export type ExperimentListItem = {
  experiment_id: number;
  symbol: string;
  strategy: string;
  parameters: Record<string, number>;
  start_date: string;
  end_date: string;
  initial_cash: number;
  transaction_cost_bps: number;
  final_equity: number;
  created_at: string;
};

export type ExperimentDetail = {
  experiment_id: number;
  symbol: string;
  strategy: string;
  parameters: Record<string, number>;
  start_date: string;
  end_date: string;
  initial_cash: number;
  transaction_cost_bps: number;
  final_equity: number;
  created_at: string;
  metrics: BacktestMetrics;
  trades: Trade[];
  equity_curve: EquityPoint[];
};

export type CompareExperimentsResponse = {
  experiments: Array<{
    experiment_id: number;
    symbol: string;
    strategy: string;
    parameters: Record<string, number>;
    start_date: string;
    end_date: string;
    initial_cash: number;
    final_equity: number;
    total_return: number | null;
    annualized_return: number | null;
    annualized_volatility: number | null;
    sharpe_ratio: number | null;
    max_drawdown: number | null;
    historical_var_95: number | null;
    expected_shortfall_95: number | null;
    number_of_trades: number;
    buy_trades: number;
    sell_trades: number;
    time_in_market_pct: number;
    best_day: number | null;
    worst_day: number | null;
    average_daily_return: number | null;
  }>;
};
