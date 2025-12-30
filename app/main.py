from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from .config import settings
from .fetcher import fetch_stock_data, FetchError
from . import storage

app = FastAPI(title="stock_service")


@app.on_event("startup")
async def startup_event():
    storage.init_db(settings.DB_PATH)


@app.post("/fetch")
async def fetch_and_store(ticker: str = Query(..., description="Ticker symbol"), period: str = "5d"):
    """Fetch OHLCV for `ticker` and store in DB/CSV."""
    try:
        rows = fetch_stock_data(ticker, period=period)
    except FetchError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    inserted = storage.save_ohlcv_bulk(settings.DB_PATH, rows)
    storage.save_quote_to_csv(settings.CSV_PATH, rows)
    return JSONResponse(content={"ticker": ticker.upper(), "fetched": len(rows), "inserted": inserted})


@app.get("/last")
async def last_saved():
    q = storage.get_latest(settings.DB_PATH)
    if not q:
        raise HTTPException(status_code=404, detail="No saved quotes")
    return q


@app.get("/history")
async def history(ticker: str | None = None):
    data = storage.get_history(settings.DB_PATH, ticker)
    return {"count": len(data), "data": data}
