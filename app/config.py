import os

from dotenv import load_dotenv

load_dotenv()

def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./data/dashboard.db")

def ingestion_token() -> str:
    return os.getenv("INGESTION_TOKEN")