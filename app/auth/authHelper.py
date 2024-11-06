import datetime
from jose import jwt
import os
from surrealdb import Surreal

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status


from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 

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


# returns format User:hus842hjs98ou2i
async def GetCurrentUserIDHelper(
        token: str = Depends(oauth2_scheme), 
        db: Surreal = Depends(get_db),
    ):
    error_stack = ErrorStack()

    try:
        try:
            user_id = VerifyAccessTokenHelper(token, error_stack)

        except Exception as e:
            if str(e) == "500: Signature has expired.":
                print("this")
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
                    f"((SELECT * FROM User "
                    f"WHERE id = 'User:{user_id}'"
                    f").id)[0];"
                )
                        
            select_user_result = DatabaseErrorHelper(query_result[0]['result'], error_stack)

            if select_user_result == None:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "select_user_result == None",
                    "None",
                    GetCurrentUserIDHelper
                )
            
            return select_user_result
        
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Querry error.",
                    e,
                    GetCurrentUserIDHelper
                )
        
    except Exception as e:
        ExceptionHelper(GetCurrentUserIDHelper, e, error_stack)
