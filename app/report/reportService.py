from fastapi import HTTPException, status

from app.auth.authService import ReturnAccessTokenHelper
from app.db.database import DatabaseResultService
from app.statement.statementService import get_statement_service

'''-> get body_part(check), condition (deleted), patient_id (ceck) from statements and images - check'''
# maybe change this row of create/relate statements to one connected query so it also gets automatically deleted 
async def CreateReportService(reportin, current_user_id, db):
    try:
        text = reportin.report_text
        index = 0
        statement_location_list = []
        
        # extract statements from text
        while True:
            index = text.find("[Statement:", index)
            if index == -1:
                break

            statement_location_list.append(index)

            reportin.statement_id_array.append(text[index+1:index+31])  

            index += 1

        # extract body_part from Statement
        body_part_query_result = await db.query(
                f"SELECT body_part FROM Statement "
                f"WHERE id = {reportin.statement_id_array[0]}"
            )

        reportin.body_part = body_part_query_result[0]['result'][0]['body_part']

        # verify patient is users
        try:
            patient_query_result = await db.query(
                f"SELECT * FROM Patient WHERE "
                f"id = {reportin.patient_id} AND "
                f"(SELECT * FROM Treated_By WHERE "
                f"out = {current_user_id});"
            )

            DatabaseResultService(patient_query_result)

            patient_data = patient_query_result[0]['result'][0]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Zeroth Database operation didnt work. {e}")
        
        # generate text
        text_with_replaced_statement = text

        while len(statement_location_list) > 0 and len(reportin.statement_id_array) > 0:
            last_statement_location = statement_location_list.pop()

            last_statement = reportin.statement_id_array.pop()
            only_statement_UUID = last_statement[10:]

            get_statement_service_result = await get_statement_service(only_statement_UUID, current_user_id, db)
            statement_text = get_statement_service_result[1][0]['text']
            text_with_replaced_statement = text_with_replaced_statement[:last_statement_location] + f"{statement_text}" + text_with_replaced_statement[last_statement_location+32:]

        text_with_patient_data = f"{patient_data['name']}\n{patient_data['address']}\n{patient_data['contact_number']}\n\n{text_with_replaced_statement}"

        '''seperate concerns to relate after creating - check'''
        '''patient has to be users - check'''
        '''change in db body_type to body_part - check'''
        '''condition muss als Parameter bei Reports raus!! - check'''
        # create the report
        try: 
            create_query_result = await db.query(
                f"CREATE Report "
                f"SET body_part = '{reportin.body_part}', "
                f"report_text = '{reportin.report_text}', "
                f"patient = '{reportin.patient_id}';"
            )
        except:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Create query failed: {e}")
        
        report_id = create_query_result[0]['result'][0]['id']
        
        # relate to report
        try:
            relate_query_result = await db.query(
                f"(RELATE {current_user_id}"
                f"->Write_Reports->"
                f"{report_id}"
                f")[0].out;"
            )

            DatabaseResultService(relate_query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Relate user-report query failed {e}")
        
        # relate images
        try:
            for image in reportin.image_id_array:
                query_result = await db.query(
                    f"RELATE {image}->Images_Reports_Join->{report_id}"
                )

            DatabaseResultService(query_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Relate image-report query failed. {e}")
        
        '''return here something proper'''
        return ReturnAccessTokenHelper(current_user_id), text_with_patient_data, create_query_result[0]['result'][0]
            
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
        # get the patient_id from the report
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
        
        # check which patients the doctor has
        try: 
            query_result = await db.query(
                f"SELECT * FROM Treated_By WHERE out = {current_user_id};"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SELECT Treate_By failed: {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this Report.")
        
        # look for matches
        try: 
            for relation in query_result[0]['result']:
                try:
                    if patient_id == relation['in']:
                        try:
                            final_query_result = await db.query(
                                f"SELECT * FROM Report WHERE id = Report:{report_id};"
                            )

                            DatabaseResultService(final_query_result)

                            return ReturnAccessTokenHelper(current_user_id), final_query_result[0]['result'][0]
                            
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

        return ReturnAccessTokenHelper(current_user_id), query_result[0]['result']

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

        return ReturnAccessTokenHelper(current_user_id), query_result[0]['result']
        
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