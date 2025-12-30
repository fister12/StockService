# stock_service

Simple FastAPI service to fetch stock quotes via `yfinance` and persist to SQLite/CSV.

Project layout

- app/: application package
  - `main.py`: FastAPI entrypoint and endpoints
  # stock_service

  A small FastAPI service that fetches stock OHLCV data using `yfinance` and persists it to SQLite (and optionally CSV).

  ## Project layout

  - `app/` — application package
    - `main.py` — FastAPI entrypoint and endpoints
    - `fetcher.py` — functions that call `yfinance`
    - `storage.py` — helpers for SQLite/CSV persistence
    - `config.py` — configuration using Pydantic
  - `tests/` — pytest unit tests
  - `data/` — runtime data files (DB/CSV)
  - `images/` — example screenshots used in this README

  ## Quick start

  Prerequisites: Python 3.9+, Docker (optional)

  Run with Docker:

  ```bash
  docker build -t stock_service .
  docker run -p 8000:8000 stock_service
  ```

  Run locally (development):

  ```bash
  pip install -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ```

  Run tests:

  ```bash
  pytest -q
  ```

  ## API Endpoints

  - `POST /fetch?ticker=TSLA&period=5d` — fetch OHLCV for the given `ticker` and persist to DB/CSV.
  - `GET /last` — return the most-recent saved OHLCV row.
  - `GET /history?ticker=TSLA` — return stored history (all tickers if `ticker` omitted).

  Example curl to fetch TSLA:

  ```bash
  curl -X POST "http://localhost:8000/fetch?ticker=TSLA&period=5d"
  ```

  ## Images

  Screenshots showing Swagger UI and example responses:

  - ![Fetch request](images/Image-1Fetch.png) — Fetch form in Swagger UI
  - ![Fetch response](images/Image-2FetchResponse.png) — Example JSON response from `POST /fetch`
  - ![Last request](images/Image-3Last.png) — `GET /last` in Swagger UI
  - ![Last response](images/Image-4LastResponse.png) — Example JSON response from `GET /last`
  - ![History request](images/Image-5History.png) — `GET /history` in Swagger UI
  - ![History response](images/Image-6HistoryResponse.png) — Example JSON response from `GET /history`

  ## Decisions & trade-offs

  - SQLite is used by default for simplicity and data integrity; a UNIQUE constraint on (`ticker`, `date`) prevents duplicate rows.
  - `yfinance.download` is used for batch OHLCV retrieval and data is normalized before insertion.

  ## Scaling notes

  - For multiple tickers or higher throughput, run fetches concurrently (asyncio or background workers such as Celery/RQ) and avoid synchronous loops.
  - Use caching and rate-limiting to reduce external API calls to Yahoo Finance.
  - For production, migrate to a managed database (Postgres) and add proper migrations.

  ## Common questions

  Q: How would this scale to handle 10 tickers concurrently?

  A: Implement concurrent fetching (async tasks or worker pool). Use a scheduler or background worker to queue fetch jobs and write results to the DB concurrently. Keep the fetching code idempotent and add retries/backoff.

  Q: How would you avoid API rate limits?

  A: Batch requests where possible, add short-term caching (TTL), and stagger requests. Respect the provider's rate limits and implement exponential backoff for retries.

  Q: What’s the first architectural change for production?

  A: Move persistence to a managed DB and separate responsibilities with a queue:

  ```
  (fetcher service) --> (Redis/Kafka queue) --> (storage writer) --> (API server)
  ```

  Q: What’s a trading-related pitfall using this setup as-is?

  A: This setup uses polling and is not suitable for low-latency trading. There is no guarantee of real-time data, time synchronization, or delivery guarantees. Add monitoring, retries, and stronger guarantees before using in trading-critical systems.

  ---



