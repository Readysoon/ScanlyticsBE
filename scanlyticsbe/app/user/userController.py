from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import User
from scanlyticsbe.app.user.userService import GetCurrentUserService, DeleteUserService, PatchUserService
from scanlyticsbe.app.auth.authSchema import Password
from scanlyticsbe.app.auth.authService import GetCurrentUserIDService


'''	1.	Get user profile
	2.	Update user profile
	3.	Delete user account
	4.	Change password (when already logged in)
	5.	Get user preferences
	6.	Update user preferences
	7.	User search/listing (for admin purposes)
    '''

'''implement that users can give patients access to their data'''

router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/")
async def get_user(
        current_user = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await GetCurrentUserService(
        current_user,
        db
        )


@router.patch("/")
async def patch_user(
        userin: User,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserIDService)
    ):
    return await PatchUserService(
            userin, 
            current_user_id, 
            db
        )


@router.delete("/")
async def delete_user(
        password: Password, 
        current_user = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await DeleteUserService(   
            password,  
            current_user,
            db
        )


