from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import User
from scanlyticsbe.app.auth.authService import GetCurrentUserService

from .userService import PatchUserService


router = APIRouter(
    prefix="/user",
    tags=["user"],
)

'''implement that users can give patients access to their data'''
'''delete user'''

@router.patch("/")
async def patch_user(
        userin: User,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserService)
    ):
    return await PatchUserService(
            userin, 
            current_user_id, 
            db
        )


