
from datetime import date, datetime, timezone

from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.db.models import DailyStep, Workout
from app.db.database import get_db
from app.ingestion.apple_health_exporter import parse_apple_health_exporter_health_export, parse_apple_health_exporter_workouts_export

session = next(get_db())

def ingest(payload: dict, person_id: int) -> None:
    """
    Ingests the provided payload into the database.

    Args:
        payload (dict): The data to be ingested.
        person_id (int): The ID of the person for whom to ingest data.
    """
    try:
        if payload.get("exportInfo") and "dataTypes" in payload["exportInfo"]:
            daily_steps = parse_apple_health_exporter_health_export(payload)
            for date, steps in daily_steps.items():
                upsert_daily_steps(session, person_id, date, steps)
        elif payload.get("exportInfo") and "activityTypes" in payload["exportInfo"]:
            workouts = parse_apple_health_exporter_workouts_export(payload)
            source_id = 1 #TODO
            for workout_uuid, workout_data in workouts.items():
                upsert_workout(session, person_id, source_id, workout_data)

    except Exception as e:
        print("An error occurred during ingestion:", e)
        raise


def upsert_daily_steps(db: Session, person_id: int, date: date, steps: int) -> None:
    """
    Upserts daily steps data into the database.
    """
    statement = insert(DailyStep).values(person_id=person_id, date=date, steps=steps)
    statement = statement.on_conflict_do_update(
        index_elements=["person_id", "date"],
        set_={"steps": steps, "updated_at": datetime.now(timezone.utc)},
    )
    db.execute(statement)
    db.commit()

def upsert_workout(db: Session, person_id: int, source_id:int, workout_data: dict) -> None:
    """
    Upserts workout data into the database
    """
    statement = insert(Workout).values(
        person_id=person_id,
        date=workout_data.get("date"),
        workout_type=workout_data.get("workout_type"),
        indoor=workout_data.get("indoor"),
        active_energy_burned=workout_data.get("active_energy_burned"),
        basal_energy_burned=workout_data.get("basal_energy_burned"),
        source_id=source_id,
        workout_uuid=workout_data.get("workout_uuid"),
    )
    statement = statement.on_conflict_do_update(
        index_elements=["person_id", "workout_uuid"],
        set_={
            "date": workout_data.get("date"),
            "workout_type": workout_data.get("workout_type"),
            "indoor": workout_data.get("indoor"),
            "active_energy_burned": workout_data.get("active_energy_burned"),
            "basal_energy_burned": workout_data.get("basal_energy_burned"),
            "source_id": source_id,
            "updated_at": datetime.now(timezone.utc)
        },
    )
    print(statement)
    db.execute(statement)
    db.commit()
