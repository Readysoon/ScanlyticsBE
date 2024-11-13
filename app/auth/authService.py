from fastapi import status
from passlib.context import CryptContext
from os import getenv

from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

from .authHelper import ReturnAccessTokenHelper, VerifyAccessTokenHelper

from app.email.emailService import EmailVerificationService
from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


'''potential security risk'''
# before creating an account the mail should be checked so the user doesnt fill out the whole signup form just to be rejected
async def CheckMailService(user_email, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                """
                SELECT VALUE email 
                FROM User 
                WHERE email = $email;
                """,
                {
                    "email": user_email.user_email
                }
            )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                CheckMailService
            )
        
        email = query_result[0]['result']
        
        if email:
            return JSONResponse(
                    status_code=409, 
                    content=[
                        {
                            "message": "Email in use."
                        }
                        ]
                    )
        
        else:
            return JSONResponse(
                    status_code=200, 
                    content=[
                        {
                            "message": "Email can be used."
                        }
                        ]
                    )
                     
    except Exception as e:
        ExceptionHelper(CheckMailService, e, error_stack)


# an user can only exist within an organization -> the first creates it, the others join
'''logic for joining an organization has to be yet implemented'''
async def OrgaSignupService(user_in, db, error_stack):

    hashed_password = pwd_context.hash(user_in.user_password)

    try: 
        try:
            query_result = await db.query(
            """
                CREATE User SET 
                    email = $user_email,
                    name = $user_name,
                    password = $password,
                    role = $user_role,
                    organization = (
                        (CREATE Organization SET
                            address = $org_address,
                            name = $org_name,
                            email = $org_email
                        ).id
                    )[0]
                """,
                {
                    "user_email": user_in.user_email,
                    "user_name": user_in.user_name,
                    "password": hashed_password,
                    "user_role": user_in.user_role,
                    "org_address": user_in.orga_address,
                    "org_name": user_in.orga_name,
                    "org_email": user_in.orga_email
                }
            )

            DatabaseErrorHelperResultText = DatabaseErrorHelper(query_result, error_stack)
   
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                OrgaSignupService
            )
        
        if DatabaseErrorHelperResultText is None:
            pass
        elif "already contains" in DatabaseErrorHelperResultText:
            error_stack.add_error(
                status.HTTP_409_CONFLICT,
                f"Email '{user_in.user_email}' is already registered.", 
                "None",
                OrgaSignupService
            )

        try:
            return JSONResponse(
                    status_code=201, 
                    content=[
                        {
                            "message": "User signed up with organization."
                        },
                        ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                        ]
                    )
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"ReturnAccessTokenHelper.", 
                e,
                OrgaSignupService
            )

    except Exception as e:   
        ExceptionHelper(OrgaSignupService, e, error_stack)


'''A user can only join an organization if the owner acccepts'''  
# Organization:1 is for all doctors without an practice
# Organization should be None
async def  UserSignupService(user_in, db, error_stack):

    DatabaseErrorHelperResultText = ""
     
    try:
        hashed_password = pwd_context.hash(user_in.user_password)
 
        try:       
            query_result = await db.query(
                    """
                    CREATE User SET 
                        email = $user_email,
                        name = $user_name,
                        password = $password,
                        role = $user_role,
                        organization = Organization:1
                    """,
                    {
                        "user_email": user_in.user_email,
                        "user_name": user_in.user_name,
                        "password": hashed_password,
                        "user_role": user_in.user_role
                    }
                )
            
            DatabaseErrorHelperResultText = DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.", 
                e,
                UserSignupService
            )

        if DatabaseErrorHelperResultText is None:
            pass
        elif "already contains" in DatabaseErrorHelperResultText:
            error_stack.add_error(
                status.HTTP_409_CONFLICT,
                f"Email '{user_in.user_email}' is already registered.",
                "None",
                UserSignupService
            )

        token = ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)

        token = token['access_token']

        first_name = user_in.user_name.split()[0]
    
        testing = getenv('TESTING', 'False').lower() == 'true'

        if testing == False:
            try:
                await EmailVerificationService(user_in.user_email, token, first_name, error_stack)
                return JSONResponse(
                        status_code=201, 
                        content={"message": f"Verification mail has been sent to {user_in.user_email}."}
                    )
            
            except Exception as e:
                error_stack.add_error(
                    status.HTTP_409_CONFLICT,
                    f"Email '{user_in.user_email}' is already registered.",
                    e,
                    UserSignupService
                )
        else: 
            try:
                return JSONResponse(
                    status_code=201, 
                    content=[
                        {
                            "message": "User registered."
                        },
                        ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                        ]
                    )
            
            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Returning Access Token failed.",
                    e,
                    UserSignupService
                )
            
    except Exception as e:
        ExceptionHelper(UserSignupService, e, error_stack)
    

async def LoginService(user_data, db, error_stack):
    try:
        try:
            query_result = await db.query(
                """
                SELECT 
                    id, 
                    email, 
                    password, 
                    verified 
                FROM User 
                WHERE email = $email;
                """,
                {
                    "email": user_data.user_email
                }
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.", 
                    e,
                    LoginService
                )

        if not query_result or not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    "User not found.", 
                    "None",
                    LoginService
                )
        else:
            if not query_result[0]['result'][0]['verified']:
                error_stack.add_error(
                    status.HTTP_403_FORBIDDEN,
                    "You have not verified your email.", 
                    "None",
                    LoginService
                )

            if not pwd_context.verify(user_data.user_password, query_result[0]['result'][0]['password']):
                error_stack.add_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "Wrong password.", 
                    "None",
                    LoginService
                )

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": "User logged in."
                },
                ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack),
                ]
            )

    except Exception as e:
        ExceptionHelper(LoginService, e, error_stack)

    
async def UpdatePasswordService(password, current_user_id, db, error_stack):

    hashed_password = pwd_context.hash(password.user_password)

    try:
        try:
            query_result = await db.query(
                    """
                    UPDATE (
                        SELECT id 
                        FROM User 
                        WHERE id = $user_id
                    ) 
                    SET password = $new_password;
                    """,
                    {
                        "user_id": current_user_id,
                        "new_password": hashed_password
                    }
                )
            
            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.", 
                    e,
                    UpdatePasswordService
                )
        
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": "Updated password successfully."
                    },
                    ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                    ]
                )

    except Exception as e:
        ExceptionHelper(UpdatePasswordService, e, error_stack)
    

async def ValidateService(current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                    """
                    SELECT verified, id 
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
                    ValidateService
                )

        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "No user found for this token.",
                    "None",
                    ValidateService
                )
        elif query_result[0]['result'][0]['verified'] == True:
            return JSONResponse(
                    status_code=200, 
                    content=[
                        {
                            "message": "User validated."
                        },
                        ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                        ]
                    ) 
        else:
            error_stack.add_error(
                    status.HTTP_403_FORBIDDEN,
                    "Please verify your email.",
                    "None",
                    ValidateService
                )

    except Exception as e:
        ExceptionHelper(ValidateService, e, error_stack)
     

async def VerificationService(token, db, error_stack):
    try:
        current_user_id = VerifyAccessTokenHelper(token, error_stack)

        try:
            query_result = await db.query(
                    """
                    UPDATE (
                        SELECT * 
                        FROM User 
                        WHERE id = $user_id
                    ) 
                    SET verified = true;
                    """,
                    {
                        "user_id": f"User:{current_user_id}"
                    }
                )
            
            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    VerificationService
                )
        
        return JSONResponse(
                    status_code=200, 
                    content=[
                        {
                            "message": f"User verified email '{query_result[0]['result'][0]['email']}'."
                        },
                        ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                        ]
                    ) 

    except Exception as e:
        ExceptionHelper(VerificationService, e, error_stack)

