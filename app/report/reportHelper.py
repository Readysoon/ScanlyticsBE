from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper 

async def GetAllReportsByPatientIDHelper(patient_id, current_user_id, db, error_stack):
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
                GetAllReportsByPatientIDHelper
            ) 
    return query_result[0]['result']

async def GetReportByIDHelper(report_id, current_user_id, db, error_stack):
    # get report by the report_id
    try: 
        query_result = await db.query(
            f"SELECT * FROM Report WHERE id = Report:{report_id};"
        )

        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Getting report by report_id query error.",
            e,
            GetReportByIDHelper
        )

    if not query_result[0]['result']:
        error_stack.add_error(
            status.HTTP_404_NOT_FOUND,
            "No record was found for this Report.",
            "None",
            GetReportByIDHelper
        )
    
    try:
        patient_id = query_result[0]['result'][0]['patient']
    except Exception as e:
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Query conversion error.",
            e,
            GetReportByIDHelper
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
            GetReportByIDHelper
        )
    
    if not query_result[0]['result']:
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "No patients where found for this user.",
            "None",
            GetReportByIDHelper
        )
    
    # look for matches
    try: 
        for relation in query_result[0]['result']:
            try:
                if patient_id == relation['in']:
                    print("AAA")
                    try:
                        final_query_result = await db.query(
                            f"SELECT * FROM Report WHERE id = Report:{report_id};"
                        )

                        DatabaseErrorHelper(final_query_result, error_stack)

                        return final_query_result
                        
                    except Exception as e:
                        error_stack.add_error(
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Error in 'SELECT * FROM Report WHERE id = Report:report_id'",
                            e,
                            GetReportByIDHelper
                        )
            except Exception as e:
                error_stack.add_error(
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                            "Error in 'patient_id == relation['in']'",
                            e,
                            GetReportByIDHelper
                        )
    except Exception as e:
        error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Error in 'for relation in query_result[0]['result']'",
                    e,
                    GetReportByIDHelper
                )    