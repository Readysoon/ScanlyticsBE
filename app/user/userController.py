from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.user.userSchema import User
from app.user.userService import GetCurrentUserService, DeleteUserService, PatchUserService

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


'''	1.	Get user profile - done
	2.	Update user profile - done
	3.	Delete user account - done
	4.	Change password (when already logged in) - done in auth
	5.	Get user preferences -> not needed yet
	6.	Update user preferences -> not needed yet
	7.	User search/listing (for admin purposes) - can do in surrealist
'''

'''implement that users can give patients access to their data - later'''

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
async def get_user(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetCurrentUserService(
            current_user_id,
            db,
            error_stack
        )


@router.patch("/")
async def patch_user(
        user_in: User,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await PatchUserService(
            user_in, 
            current_user_id, 
            db,
            error_stack
        )


@router.delete("/")
async def delete_user(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await DeleteUserService(   
            current_user_id,
            db,
            error_stack
        )
