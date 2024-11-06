from fastapi import APIRouter, Depends
from surrealdb import Surreal
from starlette.responses import JSONResponse

from app.db.database import get_db

from app.classifier.classifierService import ClassifyService
from app.classifier.classifierSchema import Images

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

'''"Analyzes" an image and returns a set of categories which then are used in get_statements_by category to pregenerate a report"'''

router = APIRouter(
        prefix="/classify",
        tags=["classify"],
    )


@router.get("/")
async def classify(
        image_array: Images,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await ClassifyService(
            image_array, 
            current_user_id, 
            db,
            error_stack
        )

