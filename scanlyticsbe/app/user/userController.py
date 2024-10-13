from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import User
from scanlyticsbe.app.user.userService import GetCurrentUserService, DeleteUserService, PatchUserService
from scanlyticsbe.app.auth.authSchema import Password
from scanlyticsbe.app.auth.authService import GetCurrentUserIDService


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


