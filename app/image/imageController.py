from fastapi import UploadFile, File, HTTPException, APIRouter, Depends
from surrealdb import Surreal
from fastapi import APIRouter

from app.db.database import get_db
from app.auth.authService import GetCurrentUserIDService
from app.image.imageService import UploadImageService, GetImagesByPatient, GetImageByID, DeleteImageByID, UpdateImageService
from app.image.imageSchema import Image


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
@router.get("/patient/{patient_id}")
async def get_images_by_patient(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetImagesByPatient(
            patient_id,
            current_user_id,
            db
        )


@router.get("/{image_id}")
async def get_image(
        image_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetImageByID(
            image_id,
            current_user_id,
            db
        )

@router.delete("/{image_id}")
async def delete_image(
        image_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await DeleteImageByID(
            image_id,
            current_user_id,
            db
        )

@router.patch("/{image_id}")
async def update_patient(
        image_in: Image,
        image_id: str,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserIDService)
    ):
    return await UpdateImageService(
            image_in, 
            image_id, 
            current_user_id, 
            db
        )

