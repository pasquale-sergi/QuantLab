from datetime import date

import pandas as pd
from sqlalchemy import select

from app.data.market_data_ingestion import MarketDataIngestionService
from app.db.models import Asset, Price


def test_ingestion_service_with_mocked_yfinance(db_session, monkeypatch) -> None:
    index = pd.to_datetime(["2024-01-02", "2024-01-03"])
    frame = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.5, 102.5],
            "Volume": [1000, 2000],
        },
        index=index,
    )

    def mock_download(symbol: str, start_date: date, end_date: date) -> pd.DataFrame:
        assert symbol == "AAPL"
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 4)
        return frame

    class MockTicker:
        info = {"shortName": "Apple Inc."}

    monkeypatch.setattr("app.data.market_data_ingestion.yf.Ticker", lambda _: MockTicker())

    service = MarketDataIngestionService(db_session, download_func=mock_download)
    result = service.ingest("aapl", date(2024, 1, 1), date(2024, 1, 4))

    assert result.symbol == "AAPL"
    assert result.rows_inserted == 2

    asset = db_session.scalar(select(Asset).where(Asset.symbol == "AAPL"))
    prices = db_session.scalars(select(Price).where(Price.asset_id == asset.id)).all()
    assert asset is not None
    assert asset.name == "Apple Inc."
    assert len(prices) == 2
