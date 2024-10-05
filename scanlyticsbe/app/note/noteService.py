from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import ReturnAccessTokenService
from scanlyticsbe.app.db.database import DatabaseResultService

'''Works'''
async def CreateNoteService(patient_id, note_in, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"Create PatientNote "
                f"Set symptoms = '{note_in.symptoms}', "
                f"diagnosis = '{note_in.diagnosis}', "
                f"treatment = '{note_in.treatment}', "
                f"severity = '{note_in.severity}', "
                f"is_urgent = {note_in.is_urgent}, "
                f"patient = 'Patient:{patient_id}', "
                f"user_owner = '{current_user_id}';"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"CreateNoteService: {e}")

async def GetNoteByID(note_id, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM PatientNote "
                f"WHERE id = PatientNote:{note_id} "
                f"AND user_owner = {current_user_id};"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this note.")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"GetNoteByID: {e}")
    
async def GetAllNotesByPatientID(patient_id, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM PatientNote "
                f"WHERE patient = Patient:{patient_id} "
                f"AND user_owner = {current_user_id};"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this patient.")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"GetAllNotesByPatientID: {e}")

async def UpdateNoteService():
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

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Patient didnt work: {e}")
    
async def DeleteNoteService():
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

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Patient didnt work: {e}")


