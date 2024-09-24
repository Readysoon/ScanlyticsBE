from fastapi import APIRouter, Depends
from surrealdb import Surreal

'''added 2 "" for db.database for deployed mode'''
from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import GetCurrentUserIDService

from .reportService import CreateReportService, GetReportByIDService#, UpdateReportService, GetAllReportsByPatient
from .reportSchema import CreateReport


router = APIRouter(
    prefix="/report",
    tags=["report"],
)

@router.post("/{patient_id}")
async def create_report(
        patient_id: str,
        reportin: CreateReport, 
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await CreateReportService(
            patient_id,
            reportin, 
            current_user_id, 
            db
        )

# braucht gar keine patient_id, da anhand der current_user_id geschaut werden kann, welche patienten 
# der Arzt hat und ob ein Report mit der angegebenen ID auch einen dieser Patienten listet
# => 
# 0. from the specified report get the patient id
# 1. which patients has the doctor
# 2. Look for matches

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

@router.get("/")
async def get_all_reports_by_patient_and_user(
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetAllReportsByPatient(
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