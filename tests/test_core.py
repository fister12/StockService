def test_settings_defaults():
import tempfile
import os
import pandas as pd
from unittest import mock
from app import storage
from app.config import settings
from app.fetcher import fetch_stock_data, FetchError


def test_db_init_and_save_and_read():
    with tempfile.TemporaryDirectory() as td:
        db_path = os.path.join(td, "test_quotes.db")
        storage.init_db(db_path)
        rows = [
            {
                "ticker": "TEST",
                "date": "2025-01-01T00:00:00",
                "open": 100.0,
                "high": 110.0,
                "low": 90.0,
                "close": 105.0,
                "volume": 1000,
            }
        ]
        inserted = storage.save_ohlcv_bulk(db_path, rows)
        assert inserted == 1
        # duplicate insert
        inserted2 = storage.save_ohlcv_bulk(db_path, rows)
        assert inserted2 == 0
        latest = storage.get_latest(db_path)
        assert latest is not None
        assert latest["ticker"] == "TEST"
        assert latest["close"] == 105.0


def test_settings_defaults():
    assert hasattr(settings, "DB_PATH")
    assert hasattr(settings, "CSV_PATH")
    assert settings.DEFAULT_TICKER


def test_fetcher_parses_dataframe(monkeypatch):
    # Prepare a small DataFrame similar to yfinance.download output
    df = pd.DataFrame(
        {
            "Open": [1.0, 2.0],
            "High": [1.1, 2.2],
            "Low": [0.9, 1.8],
            "Close": [1.05, 2.05],
            "Volume": [100, 200],
        },
        index=[pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02")],
    )

    with mock.patch("app.fetcher.yf.download", return_value=df):
        rows = fetch_stock_data("MOCK", period="2d", interval="1d")
        assert len(rows) == 2
        assert rows[0]["ticker"] == "MOCK"
        assert rows[0]["date"] == "2025-01-01T00:00:00"


def test_fetcher_raises_on_empty(monkeypatch):
    with mock.patch("app.fetcher.yf.download", return_value=pd.DataFrame()):
        try:
            fetch_stock_data("BAD", period="1d")
            assert False, "Expected FetchError"
        except FetchError:
            pass
