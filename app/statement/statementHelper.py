from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper 


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