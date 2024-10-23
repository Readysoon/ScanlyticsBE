from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.db.database import get_db
from app.auth.authService import GetCurrentUserIDService

from app.ml_models.ml_modelsService import GetModel
from .ml_modelsSchema import Model_IN

router = APIRouter(
        prefix="/ml_models",
        tags=["ml_models"],
        )

@router.get("/")
async def get_model(
        model_name: Model_IN,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    print("model_name", model_name)
    return await GetModel(
            model_name, 
            current_user_id, 
            db
        )

