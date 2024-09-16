from fastapi import APIRouter, Depends
from surrealdb import Surreal

'''added 2 "" for db.database for deployed mode'''
from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import GetCurrentUserIDService

from .reportService import CreateReportService, GetReportByIDService, UpdateReportService, GetAllReportsByPatientAndUserIDService
from .reportSchema import CreateReport


router = APIRouter(
    prefix="/report",
    tags=["report"],
)

@router.post("/")
async def create_report(
        patientin: CreateReport, 
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await CreateReportService(
            patientin, 
            current_user_id, 
            db
        )

@router.get("/{report_id}")
async def get_report(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetReportByIDService(
            patient_id, 
            current_user_id, 
            db
        )

@router.get("/")
async def get_all_reports_by_patient_and_user(
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetAllReportsByPatientAndUserIDService(
            current_user_id, 
            db
        )

@router.patch("/{report_id}")
async def update_reports(
        patientin: CreateReport,
        report_id: str,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserIDService)
    ):
    return await UpdateReportService(
            patientin, 
            report_id, 
            current_user_id, 
            db
        )