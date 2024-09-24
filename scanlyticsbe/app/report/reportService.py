from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import ReturnAccessTokenService
from scanlyticsbe.app.db.database import DatabaseResultHandlerService


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

            DatabaseResultHandlerService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        return ReturnAccessTokenService(query_result), query_result[0]['result'][0]
            
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Something creating the Report didnt work: {e}")
    

# braucht gar keine patient_id, da anhand der current_user_id geschaut werden kann, welche patienten 
# der Arzt hat und ob ein Report mit der angegebenen ID auch einen dieser Patienten listet
# => 
# 0. from the specified report get the patient id
# 1. which patients has the doctor
# 2. Look for matches

async def GetReportByIDService(report_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Report WHERE id = Report:{report_id};"
            )

            DatabaseResultHandlerService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database 'SELECT * FROM Report [...]' operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this Report.")
        
        patient_id = query_result[0]['result'][0]['patient']
        
        try: 
            query_result = await db.query(
                f"SELECT * FROM Treated_By WHERE out = {current_user_id};"
            )

            DatabaseResultHandlerService(query_result)
            
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

                            DatabaseResultHandlerService(final_query_result)

                            return ReturnAccessTokenService(current_user_id), final_query_result[0]['result'][0]
                            
                        except Exception as e:
                            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'SELECT * FROM Report WHERE id = Report:report_id': {e}")
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'patient_id == relation['in']': {e}")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error in 'for relation in query_result[0]['result']': {e}")
                
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"GetReportByIDService: {e}")       
# 
# async def UpdatePatientService(patientin, patient_id, current_user_id, db):
#         try:
#             try:
#                 name = patientin.patient_name
#                 date_of_birth = patientin.date_of_birth
#                 gender = patientin.gender
#                 contact_number = patientin.contact_number
#                 address = patientin.address
#                 set_string = "SET "
# 
#                 # elongate the update_string
#                 if name:
#                     set_string += f"name = '{name}', "
#                 if date_of_birth:
#                     set_string += f"date_of_birth = '{date_of_birth}', "
#                 if gender:
#                     set_string += f"gender = '{gender}', "
#                 if contact_number:
#                     set_string += f"contact_number = '{contact_number}', "
#                 if address:
#                     set_string += f"address = '{address}'"
# 
#             except Exception as e:
#                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")       
# 
#             try: 
#                 # and finally put everything together and send it
#                 query_result = await db.query(
#                         f"UPDATE ("
#                         f"SELECT * FROM Treated_By WHERE "
#                         f"out = '{current_user_id}' AND "
#                         f"in = 'Patient:{patient_id}' "
#                         f"LIMIT 1).in "
#                         f"{set_string};"
#                     )
#                 
#                 DatabaseResultHandlerService(query_result)
#    
#             except Exception as e:
#                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
# 
#             return ReturnAccessTokenService(query_result)
# 
#         except Exception as e:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the patient didnt work: {e}")
# 
# 
# async def GetAllPatientsByUserID(current_user_id, db):
#     try:
#         try: 
#             query_result = await db.query(
#                     f"SELECT in FROM "
#                     f"(SELECT * FROM "
#                     f"Treated_By WHERE "
#                     f"out = {current_user_id});"
#                 )
#             
#             DatabaseResultHandlerService(query_result)
#    
#         except Exception as e:
#             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
# 
#         return ReturnAccessTokenService(query_result)
#     
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Getting all patients didnt work: {e}")
# 
# 


        