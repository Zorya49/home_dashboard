import os

from dotenv import load_dotenv

load_dotenv()

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