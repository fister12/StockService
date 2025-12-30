import yfinance as yf
import pandas as pd
from typing import List, Dict


class FetchError(Exception):
    pass


def fetch_stock_data(ticker: str, period: str = "5d", interval: str = "1d") -> List[Dict]:
    """Fetch OHLCV data for `ticker` using yfinance.download.

    Returns list of rows with keys: ticker, date (ISO), open, high, low, close, volume
    Raises FetchError on invalid/empty results.
    """
    df: pd.DataFrame = yf.download(ticker, period=period, interval=interval, progress=False)
    # yfinance may return a pandas Series for some inputs (single-row); coerce to DataFrame
    if df is None or (isinstance(df, (pd.DataFrame, pd.Series)) and getattr(df, "empty", True)):
        raise FetchError(f"No data for ticker: {ticker}")
    if isinstance(df, pd.Series):
        df = df.to_frame().T
    rows: List[Dict] = []
    for idx, row in df.iterrows():
        date = idx
        def safe_val(s, key):
            if key not in s.index:
                return None
            val = s.get(key)
            # if val is a Series/array, pick the first non-NA element
            if isinstance(val, (pd.Series,)):
                val = val.dropna()
                if val.empty:
                    return None
                val = val.iloc[0]
            return val if not pd.isna(val) else None

        rows.append(
            {
                "ticker": ticker.upper(),
                "date": date.isoformat(),
                "open": float(safe_val(row, "Open")) if safe_val(row, "Open") is not None else None,
                "high": float(safe_val(row, "High")) if safe_val(row, "High") is not None else None,
                "low": float(safe_val(row, "Low")) if safe_val(row, "Low") is not None else None,
                "close": float(safe_val(row, "Close")) if safe_val(row, "Close") is not None else None,
                "volume": int(safe_val(row, "Volume")) if safe_val(row, "Volume") is not None else None,
            }
        )
    return rows
