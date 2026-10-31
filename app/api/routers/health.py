from typing import Annotated
from fastapi import APIRouter, Depends

from app.schemas.health import HealthMonitoringPayload, WorkoutPayload
from app.services.ingestion import ingest_health_data, ingest_workouts_data
from ..dependencies import authenticated_person_id

router = APIRouter()

@router.post("/api/v1/health", tags=['health'])
def health(payload: HealthMonitoringPayload, person_id: Annotated[int, Depends(authenticated_person_id)]):
    ingest_health_data(payload, person_id)
    
@router.post("/api/v1/workouts", tags=['health'])
def workouts(payload: WorkoutPayload, person_id: Annotated[int, Depends(authenticated_person_id)]):
    ingest_workouts_data(payload, person_id)