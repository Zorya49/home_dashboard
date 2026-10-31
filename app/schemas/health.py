from typing import Annotated, Literal
from datetime import datetime
from typing_extensions import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator
)

class ContractModel(BaseModel):
    model_config = ConfigDict(extra="allow")


# ---- Workout payload schemas ----
class WorkoutExportInfo(ContractModel):
    activity_types: list[str] = Field(alias="activityTypes")
    workout_count: int = Field(alias="workoutCount", gt=0)


class WorkoutItem(ContractModel):
    activity_type: str = Field(alias="activityType", min_length=1)
    end_date: datetime = Field(alias="endDate")
    indoor: bool = False
    source: str = Field(min_length=1)
    statistics: dict
    uuid: str = Field(min_length=1)


class WorkoutPayload(ContractModel):
    workout_export_info: WorkoutExportInfo = Field(alias="exportInfo")
    workouts: list[WorkoutItem] = Field(min_length=1)

    @model_validator(mode="after")
    def check_workout_amouunt_match(self) -> Self:
        if self.workout_export_info.workout_count !=len(self.workouts):
            raise ValueError("'workouts'list lenght must match declared 'workoutCount' value.")
        return self

# ---- Health monitoring payload schemas ----
class DailyStepsItem(ContractModel):
    date: datetime
    value: float = Field(ge=0, le=100000)

class HealthExportInfo(ContractModel):
    data_types: list[str] = Field(alias="dataTypes")

    @field_validator("data_types")
    @classmethod
    def must_contain_step_count(cls, value: list[str]) -> list[str]:
        if "stepCount" not in value:
            raise ValueError("'dataTypes' must contain 'stepCount'.")
        
        return value

class HealthMonitoringPayload(ContractModel):
    health_export_info: HealthExportInfo = Field(alias="exportInfo")
    daily_steps: list[DailyStepsItem] = Field(alias="stepCount", min_length=1)


# ---- Full request schemas ----
class WorkoutRequest(ContractModel):
    type: Literal["workouts"]
    payload: WorkoutPayload


class HealthMonitoringRequest(ContractModel):
    type: Literal["health_monitoring"]
    payload: HealthMonitoringPayload
