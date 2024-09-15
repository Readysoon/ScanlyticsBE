from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import ReturnAccessTokenService
from scanlyticsbe.app.db.database import DatabaseResultHandlerService


async def CreatePatientService(patientin, current_user_id, db):
    try:
        try:
            # Create the Patient while relating it to the current_user then Select * from the just created patient (instead of returing the relation)
            query_result = await db.query(
                f"SELECT * FROM (("
                f"RELATE ("
                f"CREATE Patient SET name = '{patientin.patient_name}', "
                f"date_of_birth = '{patientin.date_of_birth}', "
                f"gender = '{patientin.gender}', "
                f"contact_number = '{patientin.contact_number}', "
                f"address = '{patientin.address}'"
                f")->Treated_By->{current_user_id}"
                f").in)[0];"
            )

            DatabaseResultHandlerService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result'][0]
        
        return ReturnAccessTokenService(query_result), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Patient didnt work: {e}")


# Looks with the patient_id and current_user_id which patients are to user 
# with the id and returns information about the patient
async def GetPatientByID(patient_id, current_user_id, db):
    # Checking if patient is user's patient
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM ("
                f"SELECT * FROM "
                f"Treated_By WHERE "
                f"in = 'Patient:{patient_id}' "
                f"AND out = '{current_user_id}'"
                f").in;"
            )
            DatabaseResultHandlerService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this patient.")
        
        result_without_status = query_result[0]['result'][0]
  
        return ReturnAccessTokenService(query_result), result_without_status
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Looking up Patient didnt work: {e}")       

async def UpdatePatientService(patientin, patient_id, current_user_id, db):
        try:
            try:
                name = patientin.patient_name
                date_of_birth = patientin.date_of_birth
                gender = patientin.gender
                contact_number = patientin.contact_number
                address = patientin.address
                set_string = "SET "

                # elongate the update_string
                if name:
                    set_string += f"name = '{name}', "
                if date_of_birth:
                    set_string += f"date_of_birth = '{date_of_birth}', "
                if gender:
                    set_string += f"gender = '{gender}', "
                if contact_number:
                    set_string += f"contact_number = '{contact_number}', "
                if address:
                    set_string += f"address = '{address}'"
                
                set_string = set_string[:-2]

            except Exception as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")       

            try: 
                # and finally put everything together and send it
                query_result = await db.query(
                        f"UPDATE ("
                        f"SELECT * FROM Treated_By WHERE "
                        f"out = '{current_user_id}' AND "
                        f"in = 'Patient:{patient_id}' "
                        f").in "
                        f"{set_string};"
                    )
                
                DatabaseResultHandlerService(query_result)
   
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")

            return ReturnAccessTokenService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the patient didnt work: {e}")

# access token is here created from current_user_id !!!
async def GetAllPatientsByUserID(current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                    f"SELECT * FROM "
                    f"(SELECT * FROM "
                    f"Treated_By WHERE "
                    f"out = {current_user_id}"
                    f");"
                )
            print(query_result)
            DatabaseResultHandlerService(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        result_without_status = query_result[0]['result']
        print(query_result)

        return ReturnAccessTokenService(current_user_id), result_without_status
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Getting all patients didnt work: {e}")
    

# Tested: Deleting the Patient automatically deletes the Treated_By relation too
async def DeletePatientService(patient_id, db, current_user_id):
    try:
        try: 
            query_result = await db.query(
                    f"DELETE "
                    f"(SELECT * FROM "
                    f"Treated_By WHERE "
                    f"in = {patient_id} and "
                    f"out = {current_user_id}).in;"
                )

            # DELETE (SELECT * FROM Treated_By WHERE in = Patient:Hans9 and out = User:bsb2xdhxgn0arxgjp8mq).in;
            
            DatabaseResultHandlerService(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        if query_result[0] == '':
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Patient was deleted successfully.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Patient deletion didnt work: {e}")
    



        