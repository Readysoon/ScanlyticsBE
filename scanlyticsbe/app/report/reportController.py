from fastapi import APIRouter, Depends
from surrealdb import Surreal

'''added 2 "" for db.database for deployed mode'''
from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import ReturnAccessTokenService

from .reportService import CreateReportService, GetReportByID, UpdateReportService, GetAllReportsByPatientAndUserID
from .reportSchema import CreateReport


router = APIRouter(
    prefix="/report",
    tags=["report"],
)

@router.post("/")
async def create_report(
        patientin: CreateReport, 
        current_user_id = Depends(ReturnAccessTokenService),
        db: Surreal = Depends(get_db)
    ):
    return await CreateReportService(
            patientin, 
            current_user_id, 
            db
        )

# rename this to something more checking if a patient is actually a user's
@router.get("/{patient_id}")
async def get_report(
        patient_id: str,
        current_user_id = Depends(ReturnAccessTokenService),
        db: Surreal = Depends(get_db)
    ):
    return await GetReportByID(
            patient_id, 
            current_user_id, 
            db
        )

@router.get("/")
async def get_all_reports_by_patient_and_user(
        current_user_id = Depends(ReturnAccessTokenService),
        db: Surreal = Depends(get_db)
    ):
    return await GetAllReportsByPatientAndUserID(
            current_user_id, 
            db
        )

@router.patch("/{report_id}")
async def update_reports(
        patientin: CreateReport,
        report_id: str,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(ReturnAccessTokenService)
    ):
    return await UpdateReportService(
            patientin, 
            report_id, 
            current_user_id, 
            db
        )