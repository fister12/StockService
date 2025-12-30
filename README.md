# stock_service

Simple FastAPI service to fetch stock quotes via `yfinance` and persist to SQLite/CSV.

Project layout

- app/: application package
  - `main.py`: FastAPI entrypoint and endpoints
  - `fetcher.py`: yfinance interaction
  - `storage.py`: SQLite/CSV helpers
  - `config.py`: settings via pydantic
- tests/: pytest unit tests
- data/: runtime data files (DB/CSV)

Quick start



```

Docker

```bash
docker build -t stock_service .
docker run -p 8000:8000 stock_service
```

Tests

```bash
pytest -q
```

API Endpoints

- `POST /fetch?ticker=TSLA&period=5d` : fetch OHLCV for the given ticker and persist to DB/CSV.
- `GET /last` : returns the most-recent saved OHLCV row.
- `GET /history?ticker=TSLA` : returns stored history (all tickers if `ticker` omitted).

Images

The following screenshots illustrate the UI and example responses for the main endpoints.

- ![Fetch request](images/Image-1Fetch.png)  Fetch form in Swagger UI
- ![Fetch response](images/Image-2FetchResponse.png)  Example JSON response from `POST /fetch`
- ![Last request](images/Image-3Last.png)  `GET /last` request in Swagger UI
- ![Last response](images/Image-4LastResponse.png)  Example JSON response from `GET /last`
- ![History request](images/Image-5History.png)  `GET /history` request in Swagger UI
- ![History response](images/Image-6HistoryResponse.png)  Example JSON response from `GET /history`
Decisions & Trade-offs

- SQLite chosen over CSV to ensure data integrity and to allow a UNIQUE constraint (`ticker`,`date`) to prevent duplicates and support efficient queries.
- `yfinance.download` used for batch OHLCV retrieval and parsed into a normalized list of rows for DB insertion.

Scaling notes

- To scale to multiple tickers, run fetches concurrently using asyncio or background workers (Celery/RQ). Use caching and rate-limiting to avoid hitting Yahoo limits.
- For production, move DB to a managed store (Postgres) and add migrations.
