from fastapi import Depends, HTTPException, status
from surrealdb import Surreal
from passlib.context import CryptContext
from jose import jwt

import os
import datetime

from db.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    SECRET_KEY = os.getenv("SECRET_KEY")
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    # surreal creates an ID wrapped in ankle brackets which the following line extracts
    to_encode['sub'] = to_encode['sub'].split(":")[1].strip("⟨⟩")

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


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
      

async def signup_service(user_email, user_name, user_password, user_role, orga_address, orga_email, orga_name, db):
    orga_id = None  
    user_id = None  
    try: 
        try:
            create_orga_result = await db.query(f"CREATE Organization Set address = '{orga_address}', name = '{orga_name}', email = '{orga_email}';") 
            create_orga_status = create_orga_result[0]['status']
            create_orga_info = create_orga_result[0]['result']
            if create_orga_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail=f"{create_orga_info}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Organization didnt work: {e}")
        
        try:
            select_orga_result = await db.query(f"SELECT VALUE id FROM Organization WHERE email = '{orga_email}';")
            select_orga_info = select_orga_result[0]['result']
            orga_id = select_orga_result[0]['result'][0]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the just created Organization didnt work: {select_orga_info}")
        
        hashed_password = pwd_context.hash(user_password)
        try:
            create_user_result = await db.query(f"CREATE User:uuid() Set email = '{user_email}', name = '{user_name}', password = '{hashed_password}', role = '{user_role}', organization = '{orga_id}';")
            create_user_status = create_user_result[0]['status']
            create_user_info = create_user_result[0]['result']
            if create_user_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{create_user_info}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the User didnt work: {e}")
        
        try:
            select_user_result = await db.query(f"SELECT VALUE id FROM User WHERE email = '{user_email}';")
            user_id = select_user_result[0]['result'][0]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the user didn't work: {e}")
        
        access_token = create_access_token(data={"sub": user_id})

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        # Manual rollback: If user or organization was created, delete them
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



    