from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper, ExceptionHelper


async def GetLastStatementTextElementHelper(statement_id, db, error_stack):
    try:
        query_result = await db.query(
            f"RETURN array::len(("
            f"SELECT text FROM "
            f"Statement WHERE "
            f"id = '{statement_id}'"
            f")[0]['text']);"
        )

        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                GetLastStatementTextElementHelper
            )
        
    try:
        last_list_element = query_result[0]['result'] - 1
        
        return last_list_element
    
    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query result conversion error.",
                e,
                GetLastStatementTextElementHelper
            )
        
        
async def SearchStatementHelper(search_in, current_user_id, db, error_stack):
    try:
        try:
            search_string = ""

            # elongate the update_string
            if search_in.text:
                '''Do the sql/surreal text search magic here (instead of just this simple version)'''
                search_string += f"text = '{search_in.text}' AND "
            if search_in.section:
                search_string += f"section = '{search_in.section}' AND "
            if search_in.body_part:
                search_string += f"body_part = '{search_in.body_part}' AND "
            if search_in.medical_condition:
                search_string += f"medical_condition = '{search_in.medical_condition}' AND "
            if search_in.modality:
                search_string += f"modality = '{search_in.modality}' AND "
            
            search_string = search_string[:-5]

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Search-string creation failed.",
                e,
                SearchStatementHelper
            )
               
        try:
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE {search_string} AND "
                f"(user_owner = '{current_user_id}' OR "
                f"user_owner = 'User:1');"
            )

        except Exception as e: 
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                SearchStatementHelper
            )
        
        try: 
            result_without_status = query_result[0]['result']
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Conversion error.",
                e,
                SearchStatementHelper
            )

        result_list = []

        try:
            for result_dict in result_without_status:
                array_last_element = len(result_dict['text']) - 1
                try: 
                    query_result = await db.query(
                        f"SELECT text[{array_last_element}], * "
                        f"FROM Statement WHERE "
                        f"id = {result_dict['id']};"
                    )
                    DatabaseErrorHelper(query_result, error_stack)
                    
                    result_list.append(query_result[0]['result'][0])
        
                except Exception as e: 
                    error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Query error.",
                        e,
                        SearchStatementHelper
                    )

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Loop error.",
                e,
                SearchStatementHelper
            )
    
        if not result_list:
            error_stack.add_error(
                status.HTTP_404_NOT_FOUND,
                "Search returned no results.",
                "None",
                SearchStatementHelper
            )

        return result_list
                
    except Exception as e:
        ExceptionHelper(SearchStatementHelper, e, error_stack)


async def GetStatementByIDHelper(statement_id, current_user_id, db, error_stack):

    try: 
        query_result = await db.query(
            f"SELECT * FROM Statement "
            f"WHERE id = 'Statement:{statement_id}' "
        )
        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"First Database operation didnt work (Statement:{statement_id})",
            e,
            GetStatementByIDHelper
        )
    
    if not query_result[0]['result']:
        error_stack.add_error(
            status.HTTP_404_NOT_FOUND,
            f"No record was found for this statement.",
            "None",
            GetStatementByIDHelper
        )

    try: 
        query_result = await db.query(
        f"SELECT * FROM Statement "
        f"WHERE id = 'Statement:{statement_id}' "
        f"AND (user_owner = {current_user_id} "
        f"OR user_owner = 'User:1');"
        )
        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"First Database operation didnt work (Statement:{statement_id})",
            e,
            GetStatementByIDHelper
        )
    
    if not query_result[0]['result']:
        error_stack.add_error(
            status.HTTP_404_NOT_FOUND,
            f"You are not allowed to view this statement.",
            "None",
            GetStatementByIDHelper
        )
    
    last_text_element_number = await GetLastStatementTextElementHelper(query_result[0]['result'][0]['id'], db, error_stack)

    try: 
        query_result = await db.query(
            f"SELECT text[{last_text_element_number}],* "
            f"FROM Statement WHERE "
            f"id = '{query_result[0]['result'][0]['id']}';"
        )
        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Second Database operation didnt work (Statement:{statement_id})",
            e,
            GetStatementByIDHelper
        )
    
    result_without_status = query_result[0]['result']
    
    return result_without_status