from fastapi import HTTPException, status
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

from app.db.database import DatabaseResultHelper
from app.email.emailService import EmailVerificationService
from app.error.errorService import ErrorStack, ExceptionHelper

from app.auth.authHelper import CreateAccessTokenHelper, ReturnAccessTokenHelper, VerifyAccessTokenHelper, GetCurrentUserIDHelper


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


'''potential security risk'''
# before creating an account the mail should be checked so the user doesnt fill out the whole signup form just to be rejected
async def CheckMailService(user_email, db):
    error_stack = ErrorStack()
    query_result = None

    try:
        query_result = await db.query(
                f"SELECT VALUE email "
                f"FROM User WHERE "
                f"email = '{user_email}';"
            )
        
        DatabaseResultHelper(query_result, error_stack)
        
        email = query_result[0]['result']
        
        if email:
            return JSONResponse(status_code=226, content={"message": "Email in use."})    
        else:
            return JSONResponse(status_code=200, content={"message": "Email can be used."})    
                     
    except Exception as e:
        ExceptionHelper(CheckMailService, query_result, error_stack, e)


# an user can only exist within an organization -> the first creates it, the others join
'''logic for joining an organization has to be yet implemented'''
async def OrgaSignupService(user_in, db):
    hashed_password = pwd_context.hash(user_in.user_password)
    try: 
        try:
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_in.user_email}', "
                    f"name = '{user_in.user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_in.user_role}', "
                    f"organization = "
                    f"((CREATE Organization Set "
                    f"address = '{user_in.orga_address}', "
                    f"name = '{user_in.orga_name}', "
                    f"email = '{user_in.orga_email}'"
                    f").id)[0]"
                )
            
            DatabaseResultHelper(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation failed: {e}")  

        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:   
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user with orga didnt work: {e}")


'''A user can only join an organization if the owner acccepts'''  
# Organization:1 is for all doctors without an practice
# Organization should be None
async def UserSignupService(user_in, db):

    error_stack = ErrorStack()

    try:
        hashed_password = pwd_context.hash(user_in.user_password)

        try:       
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_in.user_email}', "
                    f"name = '{user_in.user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_in.user_role}', "
                    f"organization = Organization:1"
                )
            
            DatabaseResultHelperResultText = DatabaseResultHelper(query_result, error_stack)
   
        except Exception as e:
            raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Query error.", e, UserSignupService.__name__)

        try:
            # why did i put this if statement here?
            # if error_stack is None:
            #     pass
            # if -> elif 
            if DatabaseResultHelperResultText is None:
                pass
            elif "already contains" in DatabaseResultHelperResultText:
                return JSONResponse(status_code=409, content={"message": f"Email '{user_in.user_email}' is already registered."})
        except Exception as e:
            raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"'error_stack'/'already contains' error.", e, UserSignupService.__name__)
    

        token = ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)

        first_name = user_in.user_name.split()[0]
    
        testing = True

        if testing == False:
            try:
                await EmailVerificationService(user_in.user_email, token, first_name)
                return JSONResponse(status_code=201, content={"message": f"Verification mail has been sent to {user_in.user_email}."})
            except Exception as e:
                raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Sending mail failed.", e, UserSignupService.__name__)
        else: 
            try:
                return JSONResponse(status_code=201, content=ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack))
            except Exception as e:
                raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Returning Access Token failed.", e, UserSignupService.__name__)
            
    except Exception as e:
        ExceptionHelper(UserSignupService, error_stack, e)
    

async def LoginService(user_data, db):

    error_stack = ErrorStack()

    try:
        try:
            query_result = await db.query(
                f"SELECT id, email, password, verified "
                f"FROM User WHERE "
                f"email = '{user_data.user_email}';"
            )

            db_exception_handler = DatabaseResultHelper(query_result)
            if db_exception_handler.errors:
                for error in db_exception_handler.errors:
                    error_stack.add_error(error["code"], error["detail"], error.get("function"))

        except Exception as e:
            error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Query error.", LoginService.__name__)

        if not query_result or not query_result[0]['result']:
            error_stack.add_error(status.HTTP_404_NOT_FOUND, "User not found.", LoginService.__name__)
        else:
            if not query_result[0]['result'][0]['verified']:
                error_stack.add_error(status.HTTP_401_UNAUTHORIZED, "You have not verified your email.", LoginService.__name__)

            if not pwd_context.verify(user_data.user_password, query_result[0]['result'][0]['password']):
                error_stack.add_error(status.HTTP_401_UNAUTHORIZED, "Wrong password.", LoginService.__name__)

        if error_stack.errors:
            raise error_stack

        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        print(f"{LoginService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    
async def UpdatePasswordService(password, current_user_id, db):
    hashed_password = pwd_context.hash(password.password)
    try:
        try:
            query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT id "
                    f"FROM User WHERE "
                    f"id = '{current_user_id}') "
                    f"SET password = '{hashed_password}';"
                )
            
            DatabaseResultHelper(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        print(query_result)
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    

async def ValidateService(current_user_id, db):
    try:
        try:
            query_result = await db.query(
                    f"SELECT id "
                    f"FROM User WHERE "
                    f"id = '{current_user_id}' AND "
                    f"verified = true;"
                )
            
            DatabaseResultHelper(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    

async def VerificationService(token, db):
    error_stack = ErrorStack()
    
    try:
        current_user_id = VerifyAccessTokenHelper(token)

        try:
            query_result = await db.query(
                    f"Update ("
                    f"SELECT * "
                    f"FROM User WHERE "
                    f"id = 'User:{current_user_id}'"
                    f") SET "
                    f"verified = true;"
                )
            
            db_exception_handler = DatabaseResultHelper(query_result)
            if db_exception_handler.errors:
                for error in db_exception_handler.errors:
                    error_stack.add_error(error["code"], error["detail"], error.get("function"))
            
        except Exception as e:
            error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Query error: {e}", VerificationService.__name__)
        
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id']), {"message": f"{query_result[0]['result'][0]['email']} has been verified"}

    except Exception as e:
        print(f"{LoginService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

