import sqlite3
from pathlib import Path
import csv
from typing import Optional, List, Dict


def init_db(db_path: str) -> None:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(ticker, date)
        )
        """
    )
    conn.commit()
    conn.close()


def save_ohlcv_bulk(db_path: str, rows: List[Dict]) -> int:
    """Save list of OHLCV rows. Each row: {ticker, date, open, high, low, close, volume}.
    Uses INSERT OR IGNORE to avoid duplicates (ticker+date unique constraint).
    Returns number of inserted rows (best-effort count).
    """
    if not rows:
        return 0
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    inserted = 0
    for r in rows:
        cur.execute(
            """
            INSERT OR IGNORE INTO quotes (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                r["ticker"],
                r["date"],
                r.get("open"),
                r.get("high"),
                r.get("low"),
                r.get("close"),
                r.get("volume"),
            ),
        )
        if cur.rowcount:
            inserted += 1
    conn.commit()
    conn.close()
    return inserted


def save_quote_to_csv(csv_path: str, rows: List[Dict]) -> None:
    path = Path(csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["ticker", "date", "open", "high", "low", "close", "volume"])
        for r in rows:
            writer.writerow([
                r.get("ticker"),
                r.get("date"),
                r.get("open"),
                r.get("high"),
                r.get("low"),
                r.get("close"),
                r.get("volume"),
            ])


def get_latest(db_path: str) -> Optional[Dict]:
    if not Path(db_path).exists():
        return None
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT ticker, date, open, high, low, close, volume FROM quotes ORDER BY date DESC LIMIT 1"
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "ticker": row[0],
            "date": row[1],
            "open": row[2],
            "high": row[3],
            "low": row[4],
            "close": row[5],
            "volume": row[6],
        }
    return None


def get_history(db_path: str, ticker: Optional[str] = None) -> List[Dict]:
    if not Path(db_path).exists():
        return []
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if ticker:
        cur.execute(
            "SELECT ticker, date, open, high, low, close, volume FROM quotes WHERE ticker = ? ORDER BY date ASC",
            (ticker.upper(),),
        )
    else:
        cur.execute(
            "SELECT ticker, date, open, high, low, close, volume FROM quotes ORDER BY date ASC"
        )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "ticker": r[0],
            "date": r[1],
            "open": r[2],
            "high": r[3],
            "low": r[4],
            "close": r[5],
            "volume": r[6],
        }
        for r in rows
    ]
