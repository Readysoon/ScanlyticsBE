from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper, ExceptionHelper


async def GetLastStatementTextElementHelper(statement_id, db, error_stack):
    try:
        query_result = await db.query(
            """
            RETURN array::len((
                SELECT text 
                FROM Statement 
                WHERE id = $statement_id
            )[0]['text']);
            """,
            {
                "statement_id": statement_id
            }
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
            # Build search parameters and where conditions dynamically
            search_params = {
                "user_id": current_user_id,
                "admin_id": "User:1"  # Consider making this a constant or config value
            }
            where_conditions = []

            if search_in.text:
                where_conditions.append("text = $text")
                search_params["text"] = search_in.text
            
            if search_in.section:
                where_conditions.append("section = $section")
                search_params["section"] = search_in.section
            
            if search_in.body_part:
                where_conditions.append("body_part = $body_part")
                search_params["body_part"] = search_in.body_part
            
            if search_in.medical_condition:
                where_conditions.append("medical_condition = $condition")
                search_params["condition"] = search_in.medical_condition
            
            if search_in.modality:
                where_conditions.append("modality = $modality")
                search_params["modality"] = search_in.modality

            # Add the user condition
            where_conditions.append("(user_owner = $user_id OR user_owner = $admin_id)")

            # Construct the query
            query = f"""
                SELECT * 
                FROM Statement 
                WHERE {" AND ".join(where_conditions)};
            """

            query_result = await db.query(
                query,
                search_params
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Search query failed.",
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
                        """
                        SELECT text[$array_index], * 
                        FROM Statement 
                        WHERE id = $statement_id;
                        """,
                        {
                            "array_index": array_last_element,
                            "statement_id": result_dict['id']
                        }
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
            """
            SELECT * 
            FROM Statement 
            WHERE id = $statement_id;
            """,
            {
                "statement_id": f"Statement:{statement_id}"
            }
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
                """
                SELECT * 
                FROM Statement 
                WHERE id = $statement_id 
                AND (user_owner = $user_id 
                OR user_owner = $admin_id);
                """,
                {
                    "statement_id": f"Statement:{statement_id}",
                    "user_id": current_user_id,
                    "admin_id": "User:1"
                }
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
            """
            SELECT text[$array_index], * 
            FROM Statement 
            WHERE id = $statement_id;
            """,
            {
                "array_index": last_text_element_number,
                "statement_id": query_result[0]['result'][0]['id']
            }
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