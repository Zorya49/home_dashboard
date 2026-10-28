from datetime import date, datetime, timezone, timedelta

from sqlalchemy import extract, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import DailyStep, DataSource, Person, Workout

from app.schemas.dashboard import DashboardResponse, DashboardStepSeries, DashboardWeeklySteps, DashboardWorkoutTotal

MONTHS=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ME_EXT_ID = "me"
SPOUSE_EXT_ID = "spouse"

def get_dashboard_data() -> DashboardResponse:
    
    with SessionLocal() as session:
        step_series = fetch_monthly_steps_data(session)
        workouts = fetch_last_three_years_workout_data(session)
        last_week_steps = fetch_last_seven_days_steps_data(session)

        dashboard_data = DashboardResponse(
            year=date.today().year,
            months=MONTHS,
            stepSeries=step_series,
            workouts=workouts,
            lastSevenDays=last_week_steps,
        ) 
    return dashboard_data

def fetch_monthly_steps_data(db: Session) -> list[DashboardStepSeries]:
    current_year = date.today().year

    steps_data = db.execute(
            select(
                Person.name.label("name"),
                extract("month", DailyStep.date).label("month"),
                func.sum(DailyStep.steps).label("steps"),
            )
            .join(Person, DailyStep.person_id == Person.id)
            .where(
                DailyStep.date >= date(current_year , 1, 1)
            )
            .group_by(Person.name, extract("month", DailyStep.date).label("month"))
            .order_by(Person.name, extract("month", DailyStep.date).label("month"))
        ).all()

    me_label = get_me_label(db)
    spouse_label = get_spouse_label(db)
    monthly_steps_me, cumulative_steps_me = [], []
    monthly_steps_spouse, cumulative_steps_spouse = [], []

    for _ in range(12):
        monthly_steps_me.append(None)
        monthly_steps_spouse.append(None)

    for name, month, steps in steps_data:
        if name == me_label:
            monthly_steps_me[month-1] = steps
        if name == spouse_label:
            monthly_steps_spouse[month-1] = steps

    running_total = 0
    for steps in monthly_steps_me:
        if steps is None:
            cumulative_steps_me.append(None)
        else:
            running_total += steps
            cumulative_steps_me.append(running_total)

    running_total = 0
    for steps in monthly_steps_spouse:
        if steps is None:
            cumulative_steps_spouse.append(None)
        else:
            running_total += steps
            cumulative_steps_spouse.append(running_total)

    return [
            DashboardStepSeries(
                label=me_label,
                color="#343832",
                values=cumulative_steps_me,
            ),
            DashboardStepSeries(
                label=spouse_label,
                color="#b29748",
                values=cumulative_steps_spouse,
            ),
        ]

def fetch_last_three_years_workout_data(db: Session) -> list[DashboardWorkoutTotal]:
    current_year = date.today().year
    first_year = current_year - 2

    rows = db.execute(
        select(
            extract("year", Workout.date).label("year"),
            func.count(Workout.id).label("count"),
        )
        .join(Person, Workout.person_id == Person.id)
        .where(
            Person.external_identifier == "me",
            Workout.date >= date(first_year, 1, 1),
            Workout.date < date(current_year + 1, 1, 1),
            (((Workout.indoor == True) & (Workout.workout_type == "walking")) | (Workout.workout_type == "traditionalStrengthTraining")),
        )
        .group_by(extract("year", Workout.date))
    ).all()
    counts_by_year = {int(year): count for year, count in rows}

    return [
        DashboardWorkoutTotal(year=year, count=counts_by_year.get(year, 0))
        for year in range(first_year, current_year + 1)
    ]

def fetch_last_seven_days_steps_data(db: Session) -> list[DashboardWeeklySteps]:
    start_time = date.today() - timedelta(days=7)
    end_time = date.today() - timedelta(days=1)

    steps_data = db.execute(
        select(
            Person.name.label("name"),
            func.sum(DailyStep.steps).label("steps"),
        )
        .join(Person, DailyStep.person_id == Person.id)
        .where(
            DailyStep.date >= start_time,
            DailyStep.date <= end_time,
        )
        .group_by(Person.name)
        .order_by(Person.name)
    ).all()

    steps_by_person = {name: steps for name, steps in steps_data}
    me_label = get_me_label(db)
    spouse_label = get_spouse_label(db)

    return [
            DashboardWeeklySteps(label=me_label, count=steps_by_person.get(me_label, 0)),
            DashboardWeeklySteps(label=spouse_label, count=steps_by_person.get(spouse_label, 0)),
        ]

def get_me_label(db: Session) -> str:
    return (
        db.execute(
            select(Person.name).where(Person.external_identifier == ME_EXT_ID)
        ).scalar_one_or_none()
        or str(ME_EXT_ID)
    )

def get_spouse_label(db: Session) -> str:
    return (
            db.execute(
                select(Person.name).where(Person.external_identifier == SPOUSE_EXT_ID)
            ).scalar_one_or_none()
            or str(SPOUSE_EXT_ID)
        )