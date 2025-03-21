import datetime
from jose import jwt
import os
from surrealdb import Surreal

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper, TokenValidator

from app.db.database import get_db



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from app.error.errorHelper import ErrorStack

# use the function only in try and except block
# print(data)
# = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
def CreateAccessTokenHelper(data: dict, error_stack):

    to_encode = data.copy()
    SECRET_KEY = os.getenv("secret_key")

    if SECRET_KEY == None:
        raise error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                f"Secret key is None.", 
                e, 
                CreateAccessTokenHelper
            )

    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    # surreal creates an ID wrapped in ankle brackets which the following line extracts
    try:
        to_encode['sub'] = to_encode['sub'].split(":")[1].strip("⟨⟩")

    except Exception as e:
        raise error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                f"ID extraction didnt work.", 
                e, 
                CreateAccessTokenHelper
            )
    
    try:
        to_encode.update({"exp": expire})
    except:
        raise error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                f"Updating expire didnt work.", 
                e, 
                CreateAccessTokenHelper
            )
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

        return encoded_jwt
    
    except Exception as e:
        raise error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                f"Encoding and returning the jwt-token didnt work.", 
                e, 
                CreateAccessTokenHelper
            )


# takes current_user_id only in the format without 'User:'
def ReturnAccessTokenHelper(current_user_id, error_stack):
    try:
        # = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
        access_token = CreateAccessTokenHelper({"sub": current_user_id}, error_stack)
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                "Creating the Access Token didnt work.", 
                e, 
                ReturnAccessTokenHelper
            )



def VerifyAccessTokenHelper(token, error_stack):
    try:
        SECRET_KEY = os.getenv("secret_key")
        if SECRET_KEY == None:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "SECRET_KEY == None",
                "None",
                VerifyAccessTokenHelper
            )
            
    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Secret key couldnt be obtained",
                e,
                VerifyAccessTokenHelper
            )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        id: str = payload.get("sub")
        return id
    
    except Exception as e:
        if str(e) == "Signature has expired.":
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Signature has expired.",
                    e,
                    VerifyAccessTokenHelper
                )
        else:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Verifying the Access token didnt work.",
                e,
                VerifyAccessTokenHelper
            )

        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Decoding the payload failed",
                e,
                VerifyAccessTokenHelper
            )


# returns user_id in the format 'User:hus842hjs98ou2i'
async def GetCurrentUserIDHelper(
        raw_token: str = Depends(oauth2_scheme), 
        db: Surreal = Depends(get_db),
    ):
    error_stack = ErrorStack()
    try:
        try:
            validated_token: TokenValidator.ValidatedToken = raw_token
            
            user_id = VerifyAccessTokenHelper(validated_token, error_stack)

        except Exception as e:
            if str(e) == "500: Signature has expired.":
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Signature has expired.",
                    e,
                    GetCurrentUserIDHelper
                )
            else:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Verifying the Access token didnt work.",
                    e,
                    GetCurrentUserIDHelper
                )

        # from the id given by VerifyAccessTokenHelper the user is selected in the database
        # can also be: (SELECT id FROM User WHERE id = 'User:bsb2xdhxgn0arxgjp8mq')[0].id
        try:
            query_result = await db.query(
                """
                    SELECT * FROM User 
                    WHERE id = $user_id
                """, {
                    "user_id": f"User:{user_id}"
                })
            
            DatabaseErrorHelper(query_result, error_stack)
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error",
                e,
                GetCurrentUserIDHelper
            )

        if not query_result[0]['result']:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "No user found for this token",
                "None",
                GetCurrentUserIDHelper
            )
                                    
        last_user_id = query_result[0]['result'][0]['id']
        
        return last_user_id
        
    except Exception as e:
        ExceptionHelper(GetCurrentUserIDHelper, e, error_stack)
