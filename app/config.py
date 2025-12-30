try:
    # pydantic v1 had BaseSettings in pydantic; v2 moved it to pydantic-settings
    from pydantic_settings import BaseSettings
except Exception:
    from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DB_PATH: str = str(Path(__file__).resolve().parents[1] / "data" / "quotes.db")
    CSV_PATH: str = str(Path(__file__).resolve().parents[1] / "data" / "quotes.csv")
    DEFAULT_TICKER: str = "AAPL"
    class Config:
        env_file = ".env"

settings = Settings()
