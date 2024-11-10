from fastapi import UploadFile, File, APIRouter, Depends
from surrealdb import Surreal
from fastapi import APIRouter, Path
from typing import Annotated

from .imageService import UploadImageService, GetImagesByPatientService, GetImageByIDService, DeleteImageByIDService, UpdateImageService
from .imageSchema import Image

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
        prefix="/image",
        tags=["image"],
    )


@router.post("/{patient_id}")
async def upload_image(
        patient_id: Annotated[str, Path(min_length=20, max_length=20)],
        file: UploadFile = File(...),
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UploadImageService(
            file,
            patient_id,
            current_user_id,
            db,
            error_stack
        )


@router.get("/patient/{patient_id}")
async def get_images_by_patient(
        patient_id: Annotated[str, Path(min_length=20, max_length=20)],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetImagesByPatientService(
            patient_id,
            current_user_id,
            db,
            error_stack
        )


@router.get("/{image_id}")
async def get_image(
        image_id: Annotated[str, Path(min_length=20, max_length=20)],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetImageByIDService(
            image_id,
            current_user_id,
            db,
            error_stack
        )


@router.delete("/{image_id}")
async def delete_image(
        image_id: Annotated[str, Path(min_length=20, max_length=20)],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await DeleteImageByIDService(
            image_id,
            current_user_id,
            db,
            error_stack
        )


@router.patch("/{image_id}")
async def update_patient(
        image_in: Image,
        image_id: Annotated[str, Path(min_length=20, max_length=20)],
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserIDHelper)
    ):
    error_stack = ErrorStack()
    return await UpdateImageService(
            image_in, 
            image_id, 
            current_user_id, 
            db,
            error_stack
        )

