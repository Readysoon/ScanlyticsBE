from fastapi import UploadFile, File, HTTPException, APIRouter, Depends
from surrealdb import Surreal
from fastapi import APIRouter

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import GetCurrentUserIDService

from scanlyticsbe.app.image.imageService import UploadImageService, GetImagesByPatient


router = APIRouter(
        prefix="/image",
        tags=["image"],
    )


@router.post("/{patient_id}")
async def upload_image(
    patient_id: str,
    file: UploadFile = File(...),
    current_user_id = Depends(GetCurrentUserIDService),
    db: Surreal = Depends(get_db)
    ):
    return await UploadImageService(
        file,
        patient_id,
        current_user_id,
        db
    )

'''to do: get all images service'''
@router.get("/{patient_id}")
async def get_images_by_patient(
    patient_id: str,
    curren_user_id = Depends(GetCurrentUserIDService),
    db: Surreal = Depends(get_db)
    ):
    return await GetImagesByPatient(
        patient_id,
        curren_user_id,
        db
    )

'''to do'''
@router.get("/{filename}")
async def get_image(
    filename: str
    ):
    try:
        # Generate a URL for the uploaded file
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{filename}"
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
