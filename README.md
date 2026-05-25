# QuantLab

## Project Goal

QuantLab is a resume-focused quantitative research platform project.
The long-term goal is to support market data ingestion, PostgreSQL storage, backtesting, risk/performance analytics, and experiment tracking.

## Current Implemented Step

This step includes the initial backend, returns layer, and first risk/performance analytics layer:

- FastAPI backend service
- PostgreSQL persistence with SQLAlchemy models (`Asset`, `Price`)
- Market data ingestion with `yfinance`
- `POST /market-data/ingest`
- `GET /health`
- Daily simple returns computation from stored close prices
- Returns endpoints for one symbol and multiple symbols
- Risk/performance metrics endpoint for one symbol
- Drawdown series endpoint for one symbol

## Run with Docker Compose

From the project root (`quantlab/`):

```powershell
docker compose up --build
```

Backend API will be available at `http://localhost:8000`.

## Ingest Market Data

```powershell
curl -X POST "http://localhost:8000/market-data/ingest" `
	-H "Content-Type: application/json" `
	-d '{"symbol":"AAPL","start_date":"2020-01-01","end_date":"2020-12-31"}'
```

## Fetch Returns

### Single Symbol

```powershell
curl "http://localhost:8000/market-data/AAPL/returns?start_date=2020-01-01&end_date=2020-12-31"
```

Response shape:

```json
{
	"symbol": "AAPL",
	"start_date": "2020-01-01",
	"end_date": "2020-12-31",
	"rows": [
		{
			"date": "2020-01-02",
			"close": 75.09,
			"daily_return": null
		},
		{
			"date": "2020-01-03",
			"close": 74.36,
			"daily_return": -0.0097
		}
	]
}
```

### Multiple Symbols

```powershell
curl "http://localhost:8000/market-data/returns?symbols=AAPL,MSFT,SPY&start_date=2020-01-01&end_date=2020-12-31"
```

## Why Returns Matter

Daily returns are a core building block for quant research:

- Backtests evaluate strategy performance using return series.
- Risk metrics (volatility, drawdown, Sharpe-like measures) depend on returns.
- Comparing assets and portfolios is cleaner in return space than raw prices.

## Analytics Layer

The analytics layer computes core risk/performance metrics from daily simple returns (with 252 trading days per year and risk-free rate set to 0).

### Metric Definitions (Simple)

- `total_return`: overall compounded return across the selected date range.
- `annualized_return`: return scaled to a yearly rate assuming 252 trading days.
- `volatility`: standard deviation of daily returns.
- `annualized_volatility`: daily volatility scaled by $\sqrt{252}$.
- `sharpe_ratio`: average excess return divided by volatility (risk-free = 0).
- `max_drawdown`: worst peak-to-trough decline in the equity curve.
- `historical_var_95`: 5th percentile daily return threshold (95% historical VaR).
- `expected_shortfall_95`: average return of days at or below the VaR threshold.

### Analytics API Calls

Metrics for one symbol:

```powershell
curl "http://localhost:8000/analytics/AAPL/metrics?start_date=2020-01-01&end_date=2024-12-31"
```

Drawdown series for one symbol:

```powershell
curl "http://localhost:8000/analytics/AAPL/drawdown?start_date=2020-01-01&end_date=2024-12-31"
```

