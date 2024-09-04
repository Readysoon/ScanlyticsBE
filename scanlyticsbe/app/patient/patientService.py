from fastapi import HTTPException, status

'''added "" for db.database for deployed mode'''
from scanlyticsbe.app.auth.authService import create_access_token, get_current_user_id


async def CreatePatientService(patientin, current_user_id, db):
        try:
            create_patient_result = await db.query(
                f"CREATE Patient SET name = '{patientin.patient_name}', "
                f"date_of_birth = '{patientin.date_of_birth}', "
                f"gender = '{patientin.gender}', "
                f"contact_number = '{patientin.contact_number}', "
                f"address = '{patientin.address}';"
            )
            create_patient_status = create_patient_result[0]['status']
            create_patient_info = create_patient_result[0]['result']
            if create_patient_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{create_patient_info}")
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Patient didnt work: {e}")
        
        stripped_patient_id = create_patient_result[0]['result'][0]['id']

        try:
            connect_patient_result = await db.query(
                  f"RELATE {stripped_patient_id}->Treated_By->User:{current_user_id}"
            )
            connect_patient_status = connect_patient_result[0]['status']
            connect_patient_info = connect_patient_result[0]['result']
            if connect_patient_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{connect_patient_info}")
        except Exception as e:
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something connecting the Patient to the user didnt work: {e}")
        
        # transforming current user id to User:id for create_access_token
        current_user_id = f"User:{current_user_id}"
        
        # create the access token
        access_token = create_access_token(data={"sub": current_user_id})

        # # and return it as the final answer to the user
        return {"access_token": access_token, "token_type": "bearer"}, create_patient_result

# Looks with the patient_id and current_user_id which patients are to user 
# with the id and returns information about the patient
async def get_patient_by_id(patient_id, current_user_id, db):
    # Checking if patient is user's patient
    try:
        try: 
            check_treated_by_result = await db.query(
                f"SELECT VALUE id FROM Treated_By WHERE in = 'Patient:{patient_id}' AND out = 'User:{current_user_id}';"
            )
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Some error occured in querying the patient: {e}")

        if not check_treated_by_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this patient and user")
        
        patient_data = await db.query(
            f"SELECT * FROM Patient WHERE id = 'Patient:{patient_id}';"
        )
        return patient_data

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient was not found: {e}")       


async def UpdatePatientService(patientin, patient_id, current_user_id, db):
        # initialize and load variables with input from patientin
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
        
        # and finally put everything together and send it
        await db.query(f"UPDATE (SELECT * FROM Treated_By WHERE out = User:{current_user_id} AND in = Patient:{patient_id} LIMIT 1).out {set_string};")

        access_token = create_access_token(data={"sub": current_user_id})
        # and return it as the final answer to the user
        return {"access_token": access_token, "token_type": "bearer"}

    