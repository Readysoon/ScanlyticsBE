from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import create_access_token, GetCurrentUserService

async def CreatePatientService(patientin, current_user_id, db):
        try:
            create_patient_result = await db.query(
                f"RELATE ("
                f"CREATE Patient SET name = '{patientin.patient_name}', "
                f"date_of_birth = '{patientin.date_of_birth}', "
                f"gender = '{patientin.gender}', "
                f"contact_number = '{patientin.contact_number}', "
                f"address = '{patientin.address}'"
                f")->Treated_By->User:{current_user_id};"
            )
            create_patient_status = create_patient_result[0]['status']
            create_patient_info = create_patient_result[0]['result']
            if create_patient_status == "ERR":
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{create_patient_info}")
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Patient didnt work: {e}")
        
        try:
            # transforming current user id to User:id for create_access_token
            current_user_id = f"User:{current_user_id}"
            
            # create the access token
            access_token = create_access_token(data={"sub": current_user_id})
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Token creation failed: {e}")

        # # and return it as the final answer to the user
        return {"access_token": access_token, "token_type": "bearer"}, create_patient_result


'''Join the the two queries into one'''
# Looks with the patient_id and current_user_id which patients are to user 
# with the id and returns information about the patient
async def GetPatientByID(patient_id, current_user_id, db):
    # Checking if patient is user's patient
    try:
        try: 
            # SELECT in FROM (SELECT * FROM Treated_By WHERE out = User:{current_user_id})
            check_treated_by_result = await db.query(
                f"SELECT * FROM (SELECT * FROM Treated_By WHERE in = '{patient_id}' AND out = '{current_user_id}').in;"
            )
            print(check_treated_by_result)
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Some error occured in querying the patient: {e}")

        if not check_treated_by_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this patient and user")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient was not found: {e}")       

'''RETURN DIFF -> untested yet!!'''
async def UpdatePatientService(patientin, patient_id, current_user_id, db):
        try:
            # initialize and load variables with input from patientin
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
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")       

            try: 
                # and finally put everything together and send it
                update_patient_result = await db.query(
                    f"UPDATE ("
                    f"SELECT * FROM Treated_By WHERE "
                    f"out = 'User:{current_user_id}' AND "
                    f"in = 'Patient:{patient_id}' "
                    f"LIMIT 1).in "
                    f"{set_string};"
                    #f"RETURN DIFF;"
                    )
                print(update_patient_result)
                print(current_user_id)
                update_patient_status = update_patient_result[0]['status']
                update_patient_info = update_patient_result[0]['result']
                if update_patient_status == "ERR":
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{update_patient_info}")
                
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Creating the Patient in the database didnt work: {e}")

            try: 
                current_user_id = f"User:{current_user_id}"
                print(current_user_id)
                access_token = create_access_token(data={"sub": current_user_id})
                # and return it as the final answer to the user
                return {"access_token": access_token, "token_type": "bearer"}, update_patient_result
            except Exception as e: 
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Access creation and returning didnt work: {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the patient didnt work: {e}")



async def GetAllPatientsByUserID(current_user_id, db):
    try:
        search_result = await db.query(f"SELECT in FROM (SELECT * FROM Treated_By WHERE out = User:{current_user_id});")
        patient_search = search_result[0]['result']
        for n in patient_search:
            print(n['in'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An error occured while fetching all patients from a user: {e}")
        
    return patient_search


        