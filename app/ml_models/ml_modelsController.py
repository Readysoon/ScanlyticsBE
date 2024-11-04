from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.ml_models.ml_modelsService import RetrieveModelService
from .ml_modelsSchema import Model_IN

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db



router = APIRouter(
        prefix="/ml_models",
        tags=["ml_models"],
        )

@router.post("/")
async def retrieve_model(
        model_name: Model_IN,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    print("model_name", model_name)
    error_stack = ErrorStack()
    return await RetrieveModelService(
            model_name, 
            current_user_id, 
            db,
            error_stack
        )

