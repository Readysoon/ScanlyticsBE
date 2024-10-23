from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.db.database import get_db
from app.auth.authService import GetCurrentUserIDService

from .reportService import CreateReportService, GetReportByIDService, UpdateReportService, GetAllReportsByPatientIDService, DeleteReportService
from .reportSchema import Report


router = APIRouter(
    prefix="/report",
    tags=["report"],
)

'''TO DO: Create reports out of text and statement and patient data - '''
@router.post("/")
async def create_report(
        report_in: Report, 
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await CreateReportService(
            report_in,
            current_user_id, 
            db
        )

@router.get("/{report_id}")
async def get_report(
        report_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetReportByIDService(
            report_id,
            current_user_id, 
            db
        )

'''update to handle the new schema'''
@router.patch("/{report_id}")
async def update_report(
        report_in: Report,
        report_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await UpdateReportService(
            report_in,
            report_id, 
            current_user_id, 
            db
        )

@router.get("/all/{patient_id}")
async def get_all_reports_by_patient_and_user(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetAllReportsByPatientIDService(
            patient_id,
            current_user_id, 
            db
        )

@router.delete("/{report_id}")
async def delete_patient(
        report_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db),
    ):
    return await DeleteReportService(
            report_id,
            current_user_id,
            db
        )
