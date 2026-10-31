from math import floor
from datetime import date, datetime

from app.config import application_timezone
from app.schemas.health import HealthMonitoringPayload, WorkoutPayload

def parse_to_server_date(value: datetime) -> date:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.date()

    return value.astimezone(application_timezone()).date()


def parse_apple_health_exporter_health_export(payload: HealthMonitoringPayload) -> dict:
    """
    Parses the Apple Health export with health data (steps etc.) and returns a dictionary with the extracted data.

    Args:
        payload: JSON payload containing the Apple Health export data.

    Returns:
        dict: A dictionary with the extracted daily step counts.
    """

    daily_steps = {}

    for record in payload.daily_steps:
        date = parse_to_server_date(record.date)
        steps = record.value

        if date and steps is not None:
            daily_steps[date] = int(floor(steps))

    return daily_steps

def parse_apple_health_exporter_workouts_export(payload: WorkoutPayload) -> dict:
    """
    Parses the Apple Health export with workout data and returns a dictionary with the extracted data.

    Args:
        payload: JSON payload containing the Apple Health export data.

    Returns:
        dict: A dictionary with the extracted workouts.
    """

    workouts = {}

    for record in payload.workouts:
        date = parse_to_server_date(record.end_date)
        workout_type = record.activity_type
        indoor = record.indoor
        statistics = record.statistics
        active_energy = statistics.get("HKQuantityTypeIdentifierActiveEnergyBurned") or {}
        basal_energy = statistics.get("HKQuantityTypeIdentifierBasalEnergyBurned") or {}
        active_energy_burned = active_energy.get("sum", 0)
        basal_energy_burned = basal_energy.get("sum", 0)
        source_name = record.source
        workout_uuid = record.uuid

        if (
            date
            and workout_type
            and indoor is not None
            and source_name
            and workout_uuid
        ):
            workouts[workout_uuid] = {
                "date": date,
                "workout_type": workout_type,
                "indoor": indoor,
                "active_energy_burned": int(floor(active_energy_burned)),
                "basal_energy_burned": int(floor(basal_energy_burned)),
                "source_name": source_name,
                "workout_uuid": workout_uuid,
            }

    return workouts