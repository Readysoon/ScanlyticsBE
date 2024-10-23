from fastapi import HTTPException, status

from app.auth.authService import ReturnAccessTokenService
from app.db.database import DatabaseResultService

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

'''works'''
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

'''works'''
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


'''find a solution for updating parameter "patient" properly, maybe doctor just has to delete it?'''
'''Works - except for when wrong parameter was given'''
async def UpdateNoteService(note_in, note_id, current_user_id, db):
    try:
        try:
            symptoms = note_in.symptoms
            diagnosis = note_in.diagnosis
            treatment = note_in.treatment
            severity = note_in.severity
            is_urgent = note_in.is_urgent
            patient = note_in.patient
            set_string = "SET "

            # elongate the update_string
            if symptoms:
                set_string += f"symptoms = '{symptoms}', "
            if diagnosis:
                set_string += f"diagnosis = '{diagnosis}', "
            if treatment:
                set_string += f"treatment = '{treatment}', "
            if severity:
                set_string += f"severity = '{severity}', "
            if is_urgent:
                set_string += f"is_urgent = '{is_urgent}', "
            if patient:
                set_string += f"patient = '{patient}', "
            
            set_string = set_string[:-2]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")
        
        try:
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT * FROM PatientNote "
                    f"WHERE id = 'PatientNote:{note_id}' "
                    f"AND user_owner = {current_user_id}"
                    f") {set_string};"
                )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenService(current_user_id), result_without_status
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"UpdateNoteService: {e}")
    
    
'''works but unfinished''' 
async def DeleteNoteService(note_id, current_user_id, db):
    try:
        # try:
        #     # search before deletion
        # except: 
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        try:
            query_result = await db.query(
                f"DELETE ("
                f"SELECT * FROM PatientNote "
                f"WHERE id = PatientNote:{note_id} "
                f"AND user_owner = {current_user_id})"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        return ReturnAccessTokenService(current_user_id)
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"UpdateNoteService: {e}")


