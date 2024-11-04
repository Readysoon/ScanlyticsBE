from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper
from app.statement.statementService import GetStatementByIDService

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


'''-> get body_part(check), condition (deleted), patient_id (ceck) from statements and images - check'''
# maybe change this row of create/relate statements to one connected query so it also gets automatically deleted 
'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation
status.HTTP_400_BAD_REQUEST  # for invalid report data
status.HTTP_404_NOT_FOUND  # when referenced patient/statement not found
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid statement format
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def CreateReportService(reportin, current_user_id, db, error_stack):
    try:
        text = reportin.report_text
        index = 0
        statement_location_list = []

        try:
            # extract statements from text
            while True:
                index = text.find("[Statement:", index)
                if index == -1:
                    break

                statement_location_list.append(index)

                reportin.statement_id_array.append(text[index+1:index+31])  

                index += 1

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Exctract statements from text error.",
                e,
                CreateReportService
            )
        
        try:
            # extract body_part from Statement
            body_part_query_result = await db.query(
                    f"SELECT body_part FROM Statement "
                    f"WHERE id = {reportin.statement_id_array[0]}"
                )

            DatabaseErrorHelper(patient_query_result, error_stack)

            reportin.body_part = body_part_query_result[0]['result'][0]['body_part']
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "extract body_part from Statement query error",
                e,
                CreateReportService
            )

        # verify patient is users
        try:
            patient_query_result = await db.query(
                f"SELECT * FROM Patient WHERE "
                f"id = {reportin.patient_id} AND "
                f"(SELECT * FROM Treated_By WHERE "
                f"out = {current_user_id});"
            )

            DatabaseErrorHelper(patient_query_result, error_stack)

            patient_data = patient_query_result[0]['result'][0]

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Verify Patient is users Query Error.",
                e,
                CreateReportService
            )
        
        try:
            # generate text
            text_with_replaced_statement = text

            while len(statement_location_list) > 0 and len(reportin.statement_id_array) > 0:
                last_statement_location = statement_location_list.pop()

                last_statement = reportin.statement_id_array.pop()
                only_statement_UUID = last_statement[10:]

                GetStatementByIDService_result = await GetStatementByIDService(only_statement_UUID, current_user_id, db)
                statement_text = GetStatementByIDService_result[1][0]['text']
                text_with_replaced_statement = text_with_replaced_statement[:last_statement_location] + f"{statement_text}" + text_with_replaced_statement[last_statement_location+32:]

            text_with_patient_data = f"{patient_data['name']}\n{patient_data['address']}\n{patient_data['contact_number']}\n\n{text_with_replaced_statement}"
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Text generation error.",
                e,
                CreateReportService
            )


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

            DatabaseErrorHelper(create_query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Report creation query error.",
                e,
                CreateReportService
            )
        
        report_id = create_query_result[0]['result'][0]['id']
        
        # relate to report
        try:
            relate_query_result = await db.query(
                f"(RELATE {current_user_id}"
                f"->Write_Reports->"
                f"{report_id}"
                f")[0].out;"
            )

            DatabaseErrorHelper(relate_query_result, error_stack)
            
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Report relation query error.",
                e,
                CreateReportService
            )
        
        # relate images
        try:
            for image in reportin.image_id_array:
                query_result = await db.query(
                    f"RELATE {image}->Images_Reports_Join->{report_id}"
                )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Image relation query error.",
                e,
                CreateReportService
            )
        
        '''return here something proper'''
        return ReturnAccessTokenHelper(current_user_id, error_stack), text_with_patient_data, create_query_result[0]['result'][0]
            
    except Exception as e:
        ExceptionHelper(CreateReportService, error_stack, e)    

# braucht gar keine patient_id, da anhand der current_user_id geschaut werden kann, welche patienten 
# der Arzt hat und ob ein Report mit der angegebenen ID auch einen dieser Patienten listet
# => 
# 0. from the specified report get the patient id
# 1. which patients has the doctor
# 2. Look for matches
# siehe auch update report
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval
status.HTTP_404_NOT_FOUND  # when report doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetReportByIDService(report_id, current_user_id, db, error_stack):
    try:
        # get the patient_id from the report
        try: 
            query_result = await db.query(
                f"SELECT * FROM Report WHERE id = Report:{report_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Getting patient id from report query error.",
                e,
                GetReportByIDService
            )

        if not query_result[0]['result']:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "No record was found for this Report.",
                "None",
                GetReportByIDService
            )
        
        try:
            patient_id = query_result[0]['result'][0]['patient']
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query conversion error.",
                e,
                GetReportByIDService
            )
        
        # check which patients the doctor has
        try: 
            query_result = await db.query(
                f"SELECT * FROM Treated_By WHERE out = {current_user_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "check which patients the doctor has - query error.",
                e,
                GetReportByIDService
            )
        
        if not query_result[0]['result']:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "No record was found for this Report.",
                "None",
                GetReportByIDService
            )
        
        # look for matches
        try: 
            for relation in query_result[0]['result']:
                try:
                    if patient_id == relation['in']:
                        try:
                            final_query_result = await db.query(
                                f"SELECT * FROM Report WHERE id = Report:{report_id};"
                            )

                            DatabaseErrorHelper(final_query_result, error_stack)

                            return ReturnAccessTokenHelper(current_user_id, error_stack), final_query_result[0]['result'][0]
                            
                        except Exception as e:
                            error_stack.add_error(
                                status.HTTP_500_INTERNAL_SERVER_ERROR,
                                "Error in 'SELECT * FROM Report WHERE id = Report:report_id'",
                                e,
                                GetReportByIDService
                            )
                except Exception as e:
                    error_stack.add_error(
                                status.HTTP_500_INTERNAL_SERVER_ERROR,
                                "Error in 'patient_id == relation['in']'",
                                e,
                                GetReportByIDService
                            )
        except Exception as e:
            error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Error in 'for relation in query_result[0]['result']'",
                        e,
                        GetReportByIDService
                    )                
    except Exception as e:
        ExceptionHelper(GetReportByIDService, error_stack, e) 

'''
# Suggested:
status.HTTP_200_OK  # for successful update
status.HTTP_404_NOT_FOUND  # when report doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def UpdateReportService(reportin, report_id, current_user_id, db, error_stack):
    try:
        checked_report_query_result = await GetReportByIDService(report_id, current_user_id, db)
        checked_report_id = checked_report_query_result[1]["id"]
    except Exception as e:
        error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Checking if the report is the users didnt work",
                        e,
                        UpdateReportService
                    )      
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
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Set-string creation failed.",
                    e,
                    UpdateReportService
                )    

        try: 
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE "
                    f"{checked_report_id} "
                    f"{set_string};"
                )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    UpdateReportService
                )    

        return ReturnAccessTokenHelper(current_user_id, error_stack), query_result[0]['result']

    except Exception as e:
        ExceptionHelper(UpdateReportService, error_stack, e) 


# in order to get all reports of a patient, i have to:
# 1. query all reports 
# 2. return all reports where the patient matches 
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array)
status.HTTP_404_NOT_FOUND  # when patient doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetAllReportsByPatientIDService(patient_id, current_user_id, db, error_stack):
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

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetAllReportsByPatientIDService
                ) 

        return ReturnAccessTokenHelper(current_user_id, error_stack), query_result[0]['result']
        
    except Exception as e: 
        ExceptionHelper(GetAllReportsByPatientIDService, error_stack, e)    

'''add Report deletion to patient deletion'''
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion (more appropriate)
status.HTTP_404_NOT_FOUND  # when report doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeleteReportService(report_id, current_user_id, db, error_stack):
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
            
            DatabaseErrorHelper(query_result, error_stack)
   
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    DeleteReportService
                ) 
            
        try:
            if query_result[0] == '':
                return JSONResponse(status_code=200, content={"message": "Report was deleted successfully."})
            
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Sending JSON Response error.",
                    e,
                    DeleteReportService
                ) 
            
    except Exception as e:
        ExceptionHelper(GetAllReportsByPatientIDService, error_stack, e)  