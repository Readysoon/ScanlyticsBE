from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.db.database import get_db
from app.auth.authService import GetCurrentUserIDHelper

from app.classifier.classifierService import classify_service
from app.classifier.classifierSchema import Images

'''"Analyzes" an image and returns a set of categories which then are used in get_statements_by category to pregenerate a report"'''

router = APIRouter(
        prefix="/classifier",
        tags=["classifier"],
    )

# rename this to something more checking if a patient is actually a user's
@router.get("/")
async def classify(
        image_array: Images,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await classify_service(
            image_array, 
            current_user_id, 
            db
        )

