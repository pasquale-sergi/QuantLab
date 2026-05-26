## QuantLab

QuantLab is a Python/FastAPI quantitative research backend for market data ingestion, backtesting, risk analytics, and experiment tracking.

## What QuantLab Can Do Today

- Ingest historical market data with `yfinance`
- Store normalized price data in PostgreSQL
- Calculate daily returns
- Calculate risk/performance metrics: Sharpe, drawdown, historical VaR, and Expected Shortfall
- Run Moving Average Crossover backtests
- Simulate trades, cash balance, share inventory, transaction costs, and equity curve
- Save backtest experiments to the database
- List saved experiments and retrieve full experiment details

## Architecture Overview

```text
Market Data Ingestion
				↓
PostgreSQL Storage
				↓
Returns + Risk Analytics
				↓
Backtesting Engine
				↓
Experiment Tracking API
```

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- yfinance
- pytest

## API Overview

- `GET /health`
- `POST /market-data/ingest`
- `GET /market-data/{symbol}/returns`
- `GET /analytics/{symbol}/metrics`
- `GET /analytics/{symbol}/drawdown`
- `POST /backtests/run`
- `GET /backtests/experiments`
- `GET /backtests/experiments/{experiment_id}`
- `GET /backtests/experiments/compare?ids=1,2,3`

## Example Workflow

1. Ingest market data for `AAPL`.
2. Run a Moving Average Crossover backtest.
3. Read the saved experiment details by ID.

### 1) Ingest AAPL data

```bash
curl -X POST "http://localhost:8000/market-data/ingest" \
	-H "Content-Type: application/json" \
	-d '{
		"symbol": "AAPL",
		"start_date": "2020-01-01",
		"end_date": "2024-12-31"
	}'
```

### 2) Run MA Crossover backtest

```bash
curl -X POST "http://localhost:8000/backtests/run" \
	-H "Content-Type: application/json" \
	-d '{
		"symbol": "AAPL",
		"start_date": "2020-01-01",
		"end_date": "2024-12-31",
		"strategy": "moving_average_crossover",
		"parameters": {"short_window": 20, "long_window": 50},
		"initial_cash": 10000,
		"transaction_cost_bps": 10
	}'
```

### 3) Fetch saved experiment

```bash
curl "http://localhost:8000/backtests/experiments/1"
```

## Why This Project Matters

QuantLab mirrors the kind of internal tooling used in quantitative research and risk analytics teams: ingest data, run systematic strategy tests, compute risk metrics, and persist experiments for reproducibility and comparison.

