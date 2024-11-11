from fastapi import status
from starlette.responses import JSONResponse

from .reportHelper import GetAllReportsByPatientIDHelper, GetReportByIDHelper

from app.auth.authService import ReturnAccessTokenHelper
from app.statement.statementHelper import GetStatementByIDHelper

from app.patient.patientHelper import GetPatientByIDHelper
from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


'''-> get body_part(check), condition (deleted), patient_id (ceck) from statements and images - check'''
# maybe change this row of create/relate statements to one connected query so it also gets automatically deleted 
'''
# Suggested: 
status.HTTP_201_CREATED  # for successful creation - check 
status.HTTP_400_BAD_REQUEST  # for invalid report data - to be done in schemas
status.HTTP_404_NOT_FOUND  # when referenced patient/statement not found - check 
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - check (for upper status)
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid statement format - not necessary
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check 
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

        # verify patient is users
        try:
            patient_query_result = await db.query(
                """
                SELECT * 
                FROM Patient 
                WHERE id = $patient_id 
                AND (
                    SELECT * 
                    FROM Treated_By 
                    WHERE out = $user_id
                );
                """,
                {
                    "patient_id": reportin.patient_id,
                    "user_id": current_user_id
                }
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

                try:
                    last_statement = reportin.statement_id_array.pop()
                    only_statement_UUID = last_statement[10:]
                except Exception as e:
                    error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "1.",
                        e,
                        CreateReportService
                    )
                
                try:
                    GetStatementByIDService_result = await GetStatementByIDHelper(only_statement_UUID, current_user_id, db, error_stack)
                    statement_text = GetStatementByIDService_result[0]['text']
                except Exception as e:
                    error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "2.",
                        e,
                        CreateReportService
                    )

                text_with_replaced_statement = text_with_replaced_statement[:last_statement_location] + f"{statement_text}" + text_with_replaced_statement[last_statement_location+32:]

            text_with_patient_data = f"{patient_data['name']}\n{patient_data['address']}\n{patient_data['contact_number']}\n\n{text_with_replaced_statement}"
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Text generation error.",
                e,
                CreateReportService
            )

        # create the report in the database 
        try: 
            create_query_result = await db.query(
                """
                CREATE Report SET 
                    body_part = $body_part,
                    report_text = $report_text,
                    patient = $patient_id;
                """,
                {
                    "body_part": reportin.body_part,
                    "report_text": reportin.report_text,
                    "patient_id": reportin.patient_id
                }
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
                """
                (RELATE $user_id
                    ->Write_Reports->
                    $report_id
                )[0].out;
                """,
                {
                    "user_id": current_user_id,
                    "report_id": report_id
                }
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
                    """
                    RELATE $image_id
                        ->Images_Reports_Join->
                        $report_id;
                    """,
                    {
                        "image_id": image,
                        "report_id": report_id
                    }
                )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Image relation query error.",
                e,
                CreateReportService
            )

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Created report '{report_id}'."
                    }, 
                    text_with_patient_data,
                    create_query_result[0]['result'][0],
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(CreateReportService, e, error_stack)    

# braucht gar keine patient_id, da anhand der current_user_id geschaut werden kann, welche patienten 
# der Arzt hat und ob ein Report mit der angegebenen ID auch einen dieser Patienten listet
# => 
# 0. from the specified report get the patient id
# 1. which patients has the doctor
# 2. Look for matches
# siehe auch update report
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval - check
status.HTTP_404_NOT_FOUND  # when report doesn't exist - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetReportByIDService(report_id, current_user_id, db, error_stack):
    try:
        report = await GetReportByIDHelper(report_id, current_user_id, db, error_stack)

        return JSONResponse(
        status_code=200, 
        content=[
            {
                "message": f"Fetched report '{report_id}'."
            }, 
            report,
            ReturnAccessTokenHelper(current_user_id, error_stack)
            ]
        )         
    except Exception as e:
        ExceptionHelper(GetReportByIDService, e, error_stack) 

'''
# Suggested:
status.HTTP_200_OK  # for successful update - check
status.HTTP_404_NOT_FOUND  # when report doesn't exist - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - check
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data - to be done in schemas
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def UpdateReportService(reportin, report_id, current_user_id, db, error_stack):
    try:
        checked_report_query_result = await GetReportByIDHelper(report_id, current_user_id, db, error_stack)

        checked_report_id = checked_report_query_result[0]["result"][0]['id']

    except Exception as e:
        error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        f"GetReportByIDHelper: {checked_report_query_result}",
                        e,
                        UpdateReportService
                    )      
    try:
        try:
            # Build update parameters and set parts dynamically
            update_params = {}
            set_parts = []

            if reportin.body_part:
                set_parts.append("body_part = $body_part")
                update_params["body_part"] = reportin.body_part
            
            if reportin.condition:
                set_parts.append("condition = $condition")
                update_params["condition"] = reportin.condition
            
            if reportin.report_text:
                set_parts.append("report_text = $report_text")
                update_params["report_text"] = reportin.report_text

            # Add the report ID parameter
            update_params["report_id"] = checked_report_id

            query_result = await db.query(
                f"""
                UPDATE $report_id 
                SET {", ".join(set_parts)};
                """,
                update_params
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Update query failed.",
                e,
                UpdateReportService
            )  
            
        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Created report '{report_id}'."
                }, 
                query_result[0]['result'],
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )

    except Exception as e:
        ExceptionHelper(UpdateReportService, e, error_stack) 


# in order to get all reports of a patient, i have to:
# 1. query all reports 
# 2. return all reports where the patient matches 
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array) - check
status.HTTP_404_NOT_FOUND  # when patient doesn't exist - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetAllReportsByPatientIDService(patient_id, current_user_id, db, error_stack):

    patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

    report_list = await GetAllReportsByPatientIDHelper(patient_id, current_user_id, db, error_stack)

    try:

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Fetched all reports about patient '{patient_id}'."
                }, 
                report_list,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
        
    except Exception as e: 
        ExceptionHelper(GetAllReportsByPatientIDService, e, error_stack)    

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

        report = await GetReportByIDHelper(report_id, current_user_id, db, error_stack)

        try: 
            query_result = await db.query(
                    """
                    DELETE (
                        SELECT * 
                        FROM Write_Reports 
                        WHERE in = $user_id 
                        AND out = $report_id
                    )[0]['out'];
                    """,
                    {
                        "user_id": current_user_id,
                        "report_id": f"Report:{report_id}"
                    }
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
            if not query_result[0]['result']:

                return JSONResponse(
                    status_code=204, 
                    content=[
                        {
                            "message": f"Deleted report '{report_id}'."
                        }, 
                        ReturnAccessTokenHelper(current_user_id, error_stack)
                        ]
                    )
            
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Sending JSON Response error.",
                    e,
                    DeleteReportService
                ) 
            
    except Exception as e:
        ExceptionHelper(GetAllReportsByPatientIDService, e, error_stack)  