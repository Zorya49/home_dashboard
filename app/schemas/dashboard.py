from pydantic import BaseModel, Field


class DashboardStepSeries(BaseModel):
    label: str
    color: str
    values: list[int | None]


class DashboardWorkoutTotal(BaseModel):
    year: int
    count: int


class DashboardWeeklySteps(BaseModel):
    label: str
    count: int


class DashboardResponse(BaseModel):
    year: int
    months: list[str]
    step_series: list[DashboardStepSeries] = Field(alias="stepSeries")
    workouts: list[DashboardWorkoutTotal]
    last_seven_days: list[DashboardWeeklySteps] = Field(alias="lastSevenDays")
