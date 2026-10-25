from app.db.database import SessionLocal, engine
from app.db.models import Base, Person

from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import insert, select
from pathlib import Path

from app.schemas.health import HealthMonitoringPayload, WorkoutPayload
from app.schemas.dashboard import DashboardResponse
from app.services.ingestion import ingest_health_data, ingest_workouts_data
from app.services.dashboard import get_dashboard_data

from app.config import ingestion_token_me, ingestion_token_spouse

APP_DIR = Path(__file__).parent

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

def authenticated_person_id(authorization: Annotated[str | None, Header()] = None) -> int:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing credentials")

    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not separator or not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if token == ingestion_token_me():
        external_identifier = "me"
    elif token == ingestion_token_spouse():
        external_identifier = "spouse"
    else:
        raise HTTPException(status_code=401, detail="Invalid token")

    with SessionLocal() as session:
        person_id = session.scalar(
            select(Person.id).where(Person.external_identifier == external_identifier)
        )

    if person_id is None:
        raise HTTPException(status_code=500, detail="Authenticated person does not exist")

    return person_id


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")

@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(APP_DIR / "templates" / "dashboard.html")

@app.get("/api/v1/dashboard", response_model=DashboardResponse)
def dashboard_data() -> DashboardResponse:
    return get_dashboard_data()

@app.post("/api/v1/health")
def health(payload: HealthMonitoringPayload, person_id: Annotated[int, Depends(authenticated_person_id)]):
    ingest_health_data(payload, person_id)
    
@app.post("/api/v1/workouts")
def workouts(payload: WorkoutPayload, person_id: Annotated[int, Depends(authenticated_person_id)]):
    ingest_workouts_data(payload, person_id)