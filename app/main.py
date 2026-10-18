from app.db.database import SessionLocal, engine
from app.db.models import Base, Person

from fastapi import FastAPI, Header, HTTPException

from app.schemas.health import HealthMonitoringPayload, WorkoutPayload
from app.services.ingestion import ingest_health_data, ingest_workouts_data

from app.config import ingestion_token

INGESTION_TOKEN = ingestion_token()
PEOPLE = {1: "Person1"}
app = FastAPI()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as session:
        for person_id, name in PEOPLE.items():
            session.merge(Person(id=person_id, name=name))

init_db()

@app.post("/api/v1/health")
def health(payload: HealthMonitoringPayload, authorization: str = Header()):
    if authorization != f"Bearer {INGESTION_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

    ingest_health_data(payload, 1)

@app.post("/api/v1/workouts")
def workouts(payload: WorkoutPayload, authorization: str = Header()):
    if authorization != f"Bearer {INGESTION_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")

    ingest_workouts_data(payload, 1)