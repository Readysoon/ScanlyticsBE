from fastapi import HTTPException, status


async def CreatePatientService(patientin, current_user_id, db):
        try:
            create_patient_result = await db.query(
                f"CREATE Patient SET name = '{patientin.patient_name}', "
                f"date_of_birth = '{patientin.date_of_birth}', "  # Note the use of {date_of_birth} without quotes
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
        
        return create_patient_result


async def get_patient_by_id(patient_id, current_user_id, db):
    # Checking if patient is user's patient
    try:
        check_treated_by_result = await db.query(
            f"SELECT * FROM Treated_By WHERE in = 'Patient:{patient_id}' AND out = 'User:{current_user_id}';"
        )
        # change this chatgpt code to your own!!!
        
        # Accessing the first item in the result
        check_treated_by_status = check_treated_by_result[0]['status']
        check_treated_by_info = check_treated_by_result[0]['result']
        
        # Check if the status indicates an error
        if check_treated_by_status == "ERR":
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{check_treated_by_info}")
        
        # Ensure there is a result and it's not empty
        if not check_treated_by_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No matching records found.")
        
        # Access the first item in the result list
        treated_by_record = check_treated_by_info[0]
        
        # Check if 'id' exists in the record
        if 'id' not in treated_by_record or not treated_by_record['id']:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ID was empty or not found: {treated_by_record}")


    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient was not found: {e}")
         

async def UpdatePatientService(patientin, current_user_id, patient_id, db):
    existing_patient = await db.get_patient_by_id(patient_id)
             