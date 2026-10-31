import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from pathlib import Path

load_dotenv()

APP_DIR = Path(__file__).parent

def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./data/dashboard.db")


def _required_token(name: str) -> str:
    token = os.getenv(name)
    if not token:
        raise RuntimeError(f"{name} must be configured")
    return token


def ingestion_token_me() -> str:
    return _required_token("INGESTION_TOKEN_ME")


def ingestion_token_spouse() -> str:
    return _required_token("INGESTION_TOKEN_SPOUSE")


def application_timezone() -> ZoneInfo:
    timezone = os.getenv("APP_TIMEZONE")
    if not timezone:
        raise RuntimeError("APP_TIMEZONE must be configured")

    try:
        return ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(f"Unknown APP_TIMEZONE: {timezone}") from exc