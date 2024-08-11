from fastapi import Depends, HTTPException, status
from surrealdb import Surreal

from passlib.context import CryptContext

from db.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
            orga_id = select_orga_result[0]['result'][0]
            print(orga_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying the just created Organization didnt work: {e}")
        
        hashed_password = pwd_context.hash(user_password)
        try:
            create_user_result = await db.query(f"CREATE User Set email = '{user_email}', name = '{user_name}', password = '{hashed_password}', role = '{user_role}', organization = '{orga_id}';")
            create_user_status = create_user_result[0]['status']
            create_user_info = create_user_result[0]['result']
            if create_user_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{create_user_info}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the User didnt work: {e}")
        
        
        
        
        return HTTPException(status_code=status.HTTP_201_CREATED, detail = 
                            f"Orga_address: '{orga_address}'"
                            f"Orga_name: '{orga_name}'"
                            f"Orga_email: '{orga_email}'"
                            f"Orga_id: '{orga_id}'"
                            f"User_email: '{user_email}'"
                            f"User_name: '{user_name}'"
                            f"Orga_role '{user_role}'"
                            )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user didnt work: {e}")



        