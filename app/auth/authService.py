from fastapi import Depends, HTTPException, status
from surrealdb import Surreal
from passlib.context import CryptContext
from jose import jwt

from fastapi.security import OAuth2PasswordBearer

import os
import datetime

from db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# this takes email and password and "logs in" meaning it checks in the database 
# if the two match and then returns the access token valid for 15 min

'''Correct: out of range ERROR for user not in database!!!'''

async def login_service(db, user_data):
    try:
        query_result = await db.query(f"SELECT id, email, password FROM User WHERE email = '{user_data.username}';")
        if not query_result[0]['result'][0]:
            # user not found
            print("user not found")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Wrong credentials")
        
        if not pwd_context.verify(user_data.password, query_result[0]['result'][0]['password']):
            print("wrong password")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong credentials")

        access_token = create_access_token(data={"sub": query_result[0]['result'][0]['id']})
        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the user didnt work: {e}")
    

def create_access_token(data: dict):
    to_encode = data.copy()
    SECRET_KEY = os.getenv("SECRET_KEY")
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    print(data)

    # surreal creates an ID wrapped in ankle brackets which the following line extracts
    to_encode['sub'] = to_encode['sub'].split(":")[1].strip("⟨⟩")

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def verify_access_token(token):
    SECRET_KEY = os.getenv("SECRET_KEY")

    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        id: str = payload.get("sub")
        print(token)
        print(f"token: {token}")
        print(f"payload: {payload}")
        print(f"id: {id}")
        # commented out because id looks like this: 66qw4jxwh113byfq4lka and is no UUID
        # token_data = TokenData(id=id)
        token_data = id

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"JWTError excpetion: Something in verify_access_token didnt work: {e}")
    
    return token_data


async def get_current_user(
        token = Depends(oauth2_scheme), 
        db: Surreal = Depends(get_db)
        ):
    # verify_access_token returns the id when given the token
    token_id = verify_access_token(token)
    # from the id given by verify_access_token the user is selected in the database
    try: 
        user = await db.query(f"SELECT * FROM User WHERE id = 'User:{token_id}';")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Querying the user in get_current_user didnt work: {e}")

    return user

async def get_current_user_id(
        token = Depends(oauth2_scheme),
        ):
    
    token_id = verify_access_token(token)

    return token_id



# before creating an account the mail should be checked so the user doesnt fill out the whole signup form just to be rejected
async def check_mail_service(user_email, db):
    try:
        result = await db.query(f"SELECT VALUE email FROM User WHERE email = '{user_email}';")
        email = result[0]['result']
        print(email)

        if email:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email in use")
        else:
            return HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Email can be registered")         
         
    except: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something querying the email didnt work")
      

# an user can only exist within an organization -> the first creates it the others join
# logic for joining has to be yet implemented
async def signup_service(user_email, user_name, user_password, user_role, orga_address, orga_email, orga_name, db):

    orga_id = None  
    user_id = None  
    try: 
        # Creates the Organizaion part
        try:
            create_orga_result = await db.query(f"CREATE Organization Set address = '{orga_address}', name = '{orga_name}', email = '{orga_email}';") 
            create_orga_status = create_orga_result[0]['status']
            create_orga_info = create_orga_result[0]['result']
            if create_orga_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail=f"{create_orga_info}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Organization didnt work: {e}")
        
        # Retrieves the Organization ID to be entered into the User
        try:
            select_orga_result = await db.query(f"SELECT VALUE id FROM Organization WHERE email = '{orga_email}';")
            select_orga_info = select_orga_result[0]['result']
            orga_id = select_orga_result[0]['result'][0]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the just created Organization didnt work: {select_orga_info}")
        
        # Creates the user together with the hashed password
        hashed_password = pwd_context.hash(user_password)
        try:
            create_user_result = await db.query(f"CREATE User Set email = '{user_email}', name = '{user_name}', password = '{hashed_password}', role = '{user_role}', organization = '{orga_id}';")
            create_user_status = create_user_result[0]['status']
            create_user_info = create_user_result[0]['result']
            if create_user_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{create_user_info}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the User didnt work: {e}")
        
        # Retrieves the User ID for access token creation
        try:
            select_user_result = await db.query(f"SELECT VALUE id FROM User WHERE email = '{user_email}';")
            user_id = select_user_result[0]['result'][0]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the user didn't work: {e}")
        
        # create the access token
        access_token = create_access_token(data={"sub": user_id})

        # and return it as the final answer to the user
        return {"access_token": access_token, "token_type": "bearer"}

    # If anything goes wrong: Main Exception and rollback deletion for Organization and User 
    except Exception as e:
        try:
            if orga_id:
                await db.query(f"DELETE FROM Organization WHERE id = '{orga_id}';")
                print(f"Rollback deleted Organization: {orga_id}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rollback deletion of Organization didnt work: {e}")

        try:
            if user_id:
                await db.query(f"DELETE FROM User WHERE id = '{user_id}';")
                print(f"Rollback deleted User: {user_id}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rollback deletion of User didnt work: {e}")
        

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user didnt work: {e}")



    