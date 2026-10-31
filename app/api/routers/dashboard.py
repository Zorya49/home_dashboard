from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import get_dashboard_data
from app.config import APP_DIR

router = APIRouter()

@router.get("/dashboard", tags=['dashboard'])
def dashboard():
    return FileResponse(APP_DIR / "templates" / "dashboard.html")

@router.get("/api/v1/dashboard", tags=['dashboard'], response_model=DashboardResponse)
def dashboard_data() -> DashboardResponse:
    return get_dashboard_data()