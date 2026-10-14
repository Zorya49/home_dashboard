from typing import Annotated, Literal
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
)

class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---- Workout payload schemas ----
class WorkoutItem(ContractModel):
    activity_type: str = Field(alias="activityType", min_length=1)
    uuid: str = Field(min_length=1)


class WorkoutPayload(ContractModel):
    activity_types: list = Field(alias="activityTypes", min_length=1)
    workouts: list[WorkoutItem] = Field(min_length=1)


# ---- Health monitoring payload schema ----
class DailyStepsItem(ContractModel):
    date: datetime
    value: int = Field(ge=0)

class HealthMonitoringPayload(ContractModel):
    data_types: list = Field(alias="dataTypes", min_length=1)
    daily_steps: list[DailyStepsItem] = Field(alias="stepCount", min_length=1)


# ---- Full request schemas ----

class WorkoutRequest(ContractModel):
    type: Literal["workouts"]
    payload: WorkoutPayload


class HealthMonitoringRequest(ContractModel):
    type: Literal["health_monitoring"]
    payload: HealthMonitoringPayload



ApiRequest = Annotated[
    WorkoutRequest | HealthMonitoringRequest,
    Field(discriminator="type"),
]