from surrealdb import Surreal
from pydantic import BaseModel
from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import DatabaseResultHandlerService, ReturnAccessTokenService


'''	1.	Get user profile
	2.	Update user profile
	3.	Delete user account
	4.	Change password (when already logged in)
	5.	Get user preferences
	6.	Update user preferences
	7.	User search/listing (for admin purposes)
    '''


async def PatchUserService(userin, current_user_id, db):
    try:
        try:
            email = userin.user_email
            name = userin.user_name
            password = userin.user_password
            role = userin.user_role
            set_string = "SET "

            # elongate the update_string
            if email:
                set_string += f"email = '{email}', "
            if name:
                set_string += f"name = '{name}', "
            if password:
                set_string += f"date_of_birth = '{password}', "
            if role:
                set_string += f"gender = '{role}', "

            set_string = set_string[:-2]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")   
        
        try: 
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE "
                    f"{current_user_id} "
                    f"{set_string};"
                )
            
            DatabaseResultHandlerService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        return ReturnAccessTokenService(query_result)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the user didnt work: {e}")
