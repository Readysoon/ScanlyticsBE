from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import ReturnAccessTokenService
from scanlyticsbe.app.db.database import DatabaseResultService


async def CreateReportService(patientin, reportin, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM ("
                f"RELATE {current_user_id}"
                f"->Write_Reports->"
                f"CREATE Report "
                f"SET body_type = '{reportin.body_type}', "
                f"condition = '{reportin.condition}', "
                f"report_text = '{reportin.report_text}', "
                f"patient = 'Patient:{patientin}'"
                f")[0].out;"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        return ReturnAccessTokenService(current_user_id), query_result[0]['result']
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Report didnt work: {e}")
    

# braucht gar keine patient_id, da anhand der current_user_id geschaut werden kann, welche patienten 
# der Arzt hat und ob ein Report mit der angegebenen ID auch einen dieser Patienten listet
# => 
# 0. from the specified report get the patient id
# 1. which patients has the doctor
# 2. Look for matches
# siehe auch update report

async def GetReportByIDService(report_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Report WHERE id = Report:{report_id};"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database 'SELECT * FROM Report [...]' operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this Report.")
        
        patient_id = query_result[0]['result'][0]['patient']
        
        try: 
            query_result = await db.query(
                f"SELECT * FROM Treated_By WHERE out = {current_user_id};"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database 'SELECT * FROM Treated_By [...]' operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this Report.")
        
        try: 
            for relation in query_result[0]['result']:
                try:
                    if patient_id == relation['in']:
                        try:
                            final_query_result = await db.query(
                                f"SELECT * FROM Report WHERE id = Report:{report_id};"
                            )

                            DatabaseResultService(final_query_result)

                            return ReturnAccessTokenService(current_user_id), final_query_result[0]['result'][0]
                            
                        except Exception as e:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'SELECT * FROM Report WHERE id = Report:report_id': {e}")
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'patient_id == relation['in']': {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'for relation in query_result[0]['result']': {e}")
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"GetReportByIDService: {e}")       


async def UpdateReportService(reportin, report_id, current_user_id, db):
    try:
        checked_report_query_result = await GetReportByIDService(report_id, current_user_id, db)
        checked_report_id = checked_report_query_result[1]["id"]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Checking if the report is the users didnt work: {e}")   
    
    try:
        try:
            body_type = reportin.body_type
            condition = reportin.condition
            report_text = reportin.report_text
            set_string = "SET "

            # elongate the update_string
            if body_type:
                set_string += f"body_type = '{body_type}', "
            if condition:
                set_string += f"condition = '{condition}', "
            if report_text:
                set_string += f"report_text = '{report_text}', "

            set_string = set_string[:-2]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")       

        try: 
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE "
                    f"{checked_report_id} "
                    f"{set_string};"
                )
            
            DatabaseResultService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")

        return ReturnAccessTokenService(current_user_id), query_result[0]['result']

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the patient didnt work: {e}")


# in order to get all reports of a patient, i have to:
# 1. query all reports 
# 2. return all reports where the patient matches 
async def GetAllReportsByPatientIDService(patient_id, current_user_id, db):
    try: 
        try:
            query_result = await db.query(
                f"SELECT * FROM "
                f"Report WHERE "
                f"patient = "
                f"(SELECT * FROM "
                f"Treated_By WHERE "
                f"in = Patient:{patient_id} AND "
                f"out = {current_user_id}"
                f")[0].in;"
            )

            DatabaseResultService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")

        return ReturnAccessTokenService(current_user_id), query_result[0]['result']
        
    except Exception as e: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"GetAllReportsByPatientIDService: {e}")
    

'''add Report deletion to patient deletion'''
async def DeleteReportService(report_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                    f"DELETE ("
                    f"SELECT * FROM "
                    f"Write_Reports WHERE "
                    f"in = '{current_user_id}' AND "
                    f"out = 'Report:{report_id}'"
                    f")[0]['out'];"
                )
            
            DatabaseResultService(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        if query_result[0] == '':
            raise HTTPException(status_code=status.HTTP_200_OK, detail="Report was deleted successfully.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"DeleteReportService: {e}")