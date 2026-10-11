from math import floor
from datetime import date, datetime

def parse_date(value: str) -> date:
    if "T" in value:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date()

    return date.fromisoformat(value)


def parse_apple_health_exporter_health_export(payload) -> dict:
    """
    Parses the Apple Health export with health data (steps etc.) and returns a dictionary with the extracted data.

    Args:
        payload: JSON payload containing the Apple Health export data.

    Returns:
        dict: A dictionary with the extracted daily step counts.
    """

    daily_steps = {}

    if payload.get("exportInfo") and "stepCount" not in payload["exportInfo"].get("dataTypes", []):
        return daily_steps

    for record in payload.get("stepCount", []):
        date = parse_date(record.get("date"))
        steps = record.get("value")

        if date and steps is not None and steps >= 0 and steps <= 100000:
            daily_steps[date] = int(floor(steps))

    return daily_steps

def parse_apple_health_exporter_workouts_export(payload) -> dict:
    """
    Parses the Apple Health export with workout data and returns a dictionary with the extracted data.

    Args:
        payload: JSON payload containing the Apple Health export data.

    Returns:
        dict: A dictionary with the extracted workouts.
    """

    workouts = {}

    if payload.get("exportInfo") and not payload["exportInfo"].get("activityTypes", None):
        return workouts

    for record in payload.get("workouts", []):
        date = parse_date(record.get("endDate"))
        workout_type = record.get("activityType")
        indoor = record.get("indoor", False)
        statistics = record.get("statistics") or {}
        active_energy = statistics.get("HKQuantityTypeIdentifierActiveEnergyBurned") or {}
        basal_energy = statistics.get("HKQuantityTypeIdentifierBasalEnergyBurned") or {}
        active_energy_burned = active_energy.get("sum", 0)
        basal_energy_burned = basal_energy.get("sum", 0)
        source_name = record.get("source", "unknown")
        workout_uuid = record.get("uuid")

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