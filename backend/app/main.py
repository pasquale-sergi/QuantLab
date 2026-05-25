from fastapi import FastAPI

from app.api.routes_analytics import router as analytics_router
from app.api.routes_market_data import router as market_data_router
from app.db.database import Base, engine


app = FastAPI(title="QuantLab Backend", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(market_data_router)
app.include_router(analytics_router)
