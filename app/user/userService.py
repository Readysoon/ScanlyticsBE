from fastapi import status
from passlib.context import CryptContext
from starlette.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper
from app.patient.patientService import DeletePatientService
from app.patient.patientHelper import GetAllPatientsByUserIDHelper

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


'''	1.	Get user profile
	2.	Update user profile
	3.	Delete user account
	4.	Change password (when already logged in)
	5.	Get user preferences
	6.	Update user preferences
	7.	User search/listing (for admin purposes)
'''


'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval - check
status.HTTP_404_NOT_FOUND  # when user not found - check - done via GetCurrentUserIDService
status.HTTP_401_UNAUTHORIZED  # when token is invalid - check - done via GetCurrentUserIDService
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetCurrentUserService(current_user_id, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                """
                SELECT * 
                FROM User 
                WHERE id = $user_id;
                """,
                {
                    "user_id": current_user_id
                }
            )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetCurrentUserService
                )
            
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetching user '{current_user_id}' successfull."
                    }, 
                    query_result[0]['result'][0],
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

    except Exception  as e:
        ExceptionHelper(GetCurrentUserService, e, error_stack)
    
'''
# Suggested:
status.HTTP_200_OK  # for successful update - check
status.HTTP_400_BAD_REQUEST  # for invalid input data - to be done via schemas
status.HTTP_409_CONFLICT  # for email already in use - check
status.HTTP_422_UNPROCESSABLE_ENTITY  # for validation errors - to be done in schemas
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
'''patching mail should send new verification and set account to unverified'''
async def PatchUserService(userin, current_user_id, db, error_stack):
    try:
        try:
            # Build update parameters and set parts dynamically
            update_params = {}
            set_parts = []

            if userin.user_email:
                set_parts.append("email = $email")
                update_params["email"] = userin.user_email
            
            if userin.user_name:
                set_parts.append("name = $name")
                update_params["name"] = userin.user_name
            
            if userin.user_password:
                set_parts.append("date_of_birth = $password")  # Note: field name seems incorrect
                update_params["password"] = userin.user_password
            
            if userin.user_role:
                set_parts.append("gender = $role")  # Note: field name seems incorrect
                update_params["role"] = userin.user_role

            # Add the user ID parameter
            update_params["user_id"] = current_user_id

            query_result = await db.query(
                f"""
                UPDATE $user_id 
                SET {", ".join(set_parts)};
                """,
                update_params
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Update query failed.",
                e,
                PatchUserService
            )
            
        if query_result is None:
            pass
        elif "already contains" in query_result[0]['result']:
            error_stack.add_error(
                status.HTTP_409_CONFLICT,
                f"Email '{userin.user_email}' is already registered.", 
                "None",
                PatchUserService
            )
    
        try: 

            updated_user = query_result[0]['result'][0]

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Result conversion error.",
                    e,
                    PatchUserService
                )
            
        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Updated user '{current_user_id}'."
                }, 
                updated_user,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )

    except Exception as e:
        ExceptionHelper(PatchUserService, e, error_stack)
    
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when user not found
status.HTTP_409_CONFLICT  # when deletion fails due to dependencies
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeleteUserService(current_user_id, db, error_stack):
    try:
        query_result = await db.query(
            """
            SELECT * 
            FROM User 
            WHERE id = $user_id;
            """,
            {
                "user_id": current_user_id
            }
        )

        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Search User Query error.",
                e,
                DeleteUserService
            )

    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "No such user.",
                "None",
                DeleteUserService
            )

    try:             
        try:
            patient_list = await GetAllPatientsByUserIDHelper(current_user_id, db, error_stack)
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "GetAllPatientsByUserIDHelper.",
                e,
                DeleteUserService
            )
        
        try:
            for patient in patient_list:
                patient_id = patient['in']
                DeletePatientService(patient_id, db, current_user_id)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "DeletePatientService.",
                e,
                DeleteUserService
            )
        
        try:
            query_result = await db.query(
                """
                DELETE $user_id;
                """,
                {
                    "user_id": current_user_id
                }
            )
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Delete query error.",
                e,
                DeleteUserService
            )

        try:
            query_result = await db.query(
                """
                SELECT * 
                FROM User 
                WHERE id = $user_id;
                """,
                {
                    "user_id": current_user_id
                }
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Controll query error.",
                e,
                DeleteUserService
            )
        
        try:
            if not query_result[0]['result']:
                return JSONResponse(
                    status_code=204, 
                    content=[
                        {
                            "message": f"User deletion successful."
                        }, 
                        ReturnAccessTokenHelper(current_user_id, error_stack)
                        ]
                    )
            else: 
                return JSONResponse(
                    status_code=204, 
                    content=[
                        {
                            "message": f"User deletion unsuccessful."
                        }, 
                        ReturnAccessTokenHelper(current_user_id, error_stack)
                        ]
                    )
            
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Returning JSONResponse failed.",
                e,
                DeleteUserService
            )
        
    except Exception as e:
        ExceptionHelper(DeleteUserService, e, error_stack)