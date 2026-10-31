from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import insert, select

from app.db.database import SessionLocal, engine
from app.db.models import Base, Person
from app.config import ingestion_token_me, ingestion_token_spouse, APP_DIR
from app.api.routers import dashboard, health

USERS = [
    {"name": "Me", "external_identifier": "me"},
    {"name": "Spouse", "external_identifier": "spouse"}
]

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal.begin() as session:
        existing_identifiers = set(
            session.scalars(select(Person.external_identifier))
        )

        missing_users = [
            user for user in USERS
            if user["external_identifier"] not in existing_identifiers
        ]

        if missing_users:
            session.execute(insert(Person), missing_users)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if ingestion_token_me() == ingestion_token_spouse():
        raise RuntimeError("Ingestion tokens shall be different")

    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

app.include_router(dashboard.router)
app.include_router(health.router)
