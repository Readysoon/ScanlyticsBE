import os
from starlette.responses import JSONResponse
from fastapi import HTTPException, status

from .statementSchema import Statement
from .statementHelper import GetLastStatementTextElementHelper, SearchStatementHelper, GetStatementByIDHelper

from app.auth.authService import ReturnAccessTokenHelper
from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 

'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation - check
status.HTTP_400_BAD_REQUEST  # for invalid statement data - to be done in schema
status.HTTP_422_UNPROCESSABLE_ENTITY  # for validation errors - ?? isnt it the same
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def CreateStatementService(statement_in, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"CREATE Statement "
                f"SET text += '{statement_in.text}', "
                f"body_part = '{statement_in.body_part}', "
                f"medical_condition = '{statement_in.medical_condition}', "
                f"modality = '{statement_in.modality}', "
                f"section = '{statement_in.section}', "
                f"user_owner = '{current_user_id}';"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                GetLastStatementTextElementHelper
            )
        
        # differentiate between a statement writen by the user and by the initialization
        if current_user_id != "User:1":

            return JSONResponse(
                status_code=201, 
                content=[
                    {
                        "message": f"Created statement."
                    }, 
                    query_result[0]['result'][0],
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
                
    except Exception as e:
        ExceptionHelper(CreateStatementService, e, error_stack)  
    


'''
status.HTTP_201_CREATED  # for successful initialization - check
status.HTTP_409_CONFLICT  # when statements already exist - too much for now
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'reportTemplates')

async def InitializeStatementsService(current_user_id, db, error_stack):
    try:
        # implement checking if user is logged in - can i do it with only checking the access token in the router??
        # try:
        #     query_result = await db.query(
        #         f"SELECT * FROM Statement "
        #         f"WHERE {search_string} AND "
        #         f"(user_owner = '{current_user_id}' OR "
        #         f"user_owner = 'User:1');"
        #     )
# 
        # except Exception as e: 
        #     error_stack.add_error(
        #         status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         "Query error.",
        #         e,
        #         SearchStatementService
        #     )

        for file_name in os.listdir(TEMPLATES_DIR):
            if file_name.endswith('.txt'):
                file_path = os.path.join(TEMPLATES_DIR, file_name)
                with open(file_path, 'r', encoding='utf-8') as file:

                    base_name, _ = os.path.splitext(file_name)  # Split the file name from its extension

                    file_name_parts = base_name.split() # split Röntgen and the body_part

                    content = file.read()

                    lines = content.splitlines()  

                    statement_instance = Statement()

                    statement_instance.section = ""
                    statement_instance.body_part = file_name_parts[1]
                    statement_instance.medical_condition = "sick"
                    statement_instance.modality = file_name_parts[0]
                    statement_instance.text = ""

                    for line in lines:
                        line = line.strip()  

                        if line in ["__Indikation__", "__Technik__", "__Klinik__", "__Vergleich__", "__Befund__", "__Beurteilung__"]:
                            statement_instance.section = line

                        elif line:  
                            statement_instance.text = line
                        
                            # find some other way to check if it already in the database
                            try:
                                query_result = await db.query(
                                    f"SELECT * FROM Statement "
                                    f"WHERE text = '{statement_instance.text}' "
                                    f"AND body_part = '{statement_instance.body_part}';"
                                )
                            except Exception as e:
                                error_stack.add_error(
                                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    f"Select Statements didnt work",
                                    e,
                                    InitializeStatementsService
                                )
                                
                            try: 
                                if not query_result[0]['result'] and statement_instance.section:
                                    await CreateStatementService(statement_instance, "User:1", db, error_stack)
                            except Exception as e:
                                error_stack.add_error(
                                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    f"CreateStatementService",
                                    e,
                                    InitializeStatementsService
                                )
        
        return JSONResponse(
            status_code=201, 
            content=[
                {
                    "message": f"Statements initialized."
                }, 
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
    
    except Exception as e:
        ExceptionHelper(InitializeStatementsService, e, error_stack)  


'''works with last array elements'''
'''
# Suggested:
status.HTTP_200_OK  # for successful search (even with empty results) - check
status.HTTP_400_BAD_REQUEST  # for invalid search parameters - to be done in schema
status.HTTP_422_UNPROCESSABLE_ENTITY  # for malformed search criteria - isnt it the same???
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors  - check
'''
async def SearchStatementService(search_in, current_user_id, db, error_stack):
    try:

        result_list = await SearchStatementHelper(search_in, current_user_id, db, error_stack)

        statement_count = 0

        for statement in result_list:
            statement_count += 1

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Found {statement_count} statement(s)."
                }, 
                result_list,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
                
    except Exception as e:
        ExceptionHelper(SearchStatementService, e, error_stack)
    
'''works with last array elements'''
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval  - check
status.HTTP_404_NOT_FOUND  # keep this  - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission  - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetStatementByIDService(statement_id, current_user_id, db, error_stack):
    try:

        statement = await GetStatementByIDHelper(statement_id, current_user_id, db, error_stack)

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Fetching statement '{statement_id}' successfull."
                }, 
                statement,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
    
    except Exception as e:
        ExceptionHelper(GetStatementByIDService, e, error_stack)
    

'''works with last array elements'''
'''
# Suggested:
status.HTTP_200_OK  # for successful update - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission (instead of 401) - redundant
status.HTTP_404_NOT_FOUND  # keep this - check
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data - to be done in schemas
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetAllStatementsByUserService(current_user_id, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE user_owner = '{current_user_id}';"
            )
            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"Query error.",
                e,
                GetAllStatementsByUserService
            )
        
        if not query_result[0]['result']:
            error_stack.add_error(
                status.HTTP_404_NOT_FOUND,
                f"No record was found for this user.",
                "None",
                GetAllStatementsByUserService
            )
        
        result_without_status = query_result[0]['result']

        result_list = []

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
                    f"Query error.",
                    e,
                    GetAllStatementsByUserService
                )

        statement_count = 0

        for statement in result_list:
            statement_count += 1

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Fetched all {statement_count} statement(s) from user '{current_user_id}'."
                }, 
                result_list,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
    
    except Exception as e:
        ExceptionHelper(GetStatementByIDService, e, error_stack)

    
'''not tested after implementing User:1/other user differentation'''
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion (more appropriate) - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - check
status.HTTP_404_NOT_FOUND  # when statement doesn't exist - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def UpdateStatementService(statement_id, statement_in, current_user_id, db, error_stack):
    try:

        statement = GetStatementByIDHelper(statement_id, current_user_id, db, error_stack)

        # collect the update information
        try:
            section = statement_in.section
            body_part = statement_in.body_part
            medical_condition = statement_in.medical_condition
            modality = statement_in.modality
            text = statement_in.text
            set_string = "SET "

            # elongate the update_string
            if text:
                set_string += f"text += '{text}', "
            if section:
                set_string += f"section = '{section}', "
            if body_part:
                set_string += f"body_part = '{body_part}', "
            if medical_condition:
                set_string += f"medical_condition = '{medical_condition}', "
            if modality:
                set_string += f"modality = '{modality}', "
            
            set_string = set_string[:-2]

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Set-string creation failed.",
                    e,
                    UpdateStatementService
                )
        try:        
            # determine the statement owner
            query_result = await db.query(
                f"SELECT user_owner FROM Statement WHERE "
                f"id = 'Statement:{statement_id}' "
                f"AND (user_owner = 'User:1' "
                f"OR user_owner = '{current_user_id}'"
                f");"
                )

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Query error: {query_result}",
                    e,
                    UpdateStatementService
                )
        try:  
            statement_owner_conversed = query_result[0]['result'][0]['user_owner']
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"You cannot edit this statement.",
                    e,
                    UpdateStatementService
                )
        
        # if its a Scanlytics Statement you can only edit the text
        if statement_owner_conversed == "User:1":
            if section or body_part or medical_condition or modality:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to edit other parameters than 'text' in Scanlytics statements.")
            if text: 
                try:
                    query_result = await db.query(
                        f"UPDATE ("
                        f"SELECT * FROM Statement WHERE "
                        f"id = 'Statement:{statement_id}'"
                        f") SET text += '{text}';"
                        )
                    
                    DatabaseErrorHelper(query_result, error_stack)

                except Exception as e: 
                    if not query_result[0]['result']:
                        error_stack.add_error(
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"You are either not authorized to edit the Statement or it doesnt exist.",
                            "None",
                            UpdateStatementService
                        )
                    error_stack.add_error(
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Database operation for updating Scanlytics statement didnt work",
                            e,
                            UpdateStatementService
                        )
            else: 
                error_stack.add_error(
                            status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"You need to enter something.",
                            e,
                            UpdateStatementService
                        )
                        
        # otherwise you can update your own statement how you wish
        else: 
            try:
                # and finally put everything together and send it
                query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT * FROM Statement WHERE "
                    f"id = 'Statement:{statement_id}' "
                    f"AND user_owner = '{current_user_id}'"
                    f") {set_string};"
                    )

                DatabaseErrorHelper(query_result, error_stack)
                
            except Exception as e: 
                if not query_result[0]['result']:
                    error_stack.add_error(
                            status.HTTP_404_NOT_FOUND,
                            f"You are either not authorized to edit the Statement or it doesnt exist.",
                            "None",
                            UpdateStatementService
                        )
                error_stack.add_error(
                            status.HTTP_404_NOT_FOUND,
                            f"Database operation for Updating your own didnt work.",
                            e,
                            UpdateStatementService
                        )
        try:
            # return the Statement only displaying the last text in the array
            last_element_number = await GetLastStatementTextElementHelper(query_result[0]['result'][0]['id'], db, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"GetLastStatementTextElementHelper",
                    e,
                    UpdateStatementService
                )

        try: 
            query_result = await db.query(
                f"SELECT text[{last_element_number}],* "
                f"FROM Statement WHERE "
                f"id = '{query_result[0]['result'][0]['id']}';"
            )
            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Query error.",
                    e,
                    UpdateStatementService
                )
        
        result_without_status = query_result[0]['result']

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Updated statement '{statement_id}'."
                }, 
                result_without_status,
                ReturnAccessTokenHelper(current_user_id, error_stack)
                ]
            )
                
    except Exception as e:
        ExceptionHelper(UpdateStatementService, e, error_stack)
    
# continue from here
'''check: implement checking if deletion worked - check '''
'''implement removing all additional texts in arrays when deleting a scanlytics statement -  check'''
async def DeleteOrResetStatementService(statement_id, current_user_id, db, error_stack):
    try:

        statement = GetStatementByIDHelper(statement_id, current_user_id, db, error_stack)

        try: 
            query_result = await db.query(
                f"SELECT * FROM Statement WHERE "
                f"id = Statement:{statement_id} "
                f"AND ("
                f"user_owner = '{current_user_id}' "
                f"OR user_owner = 'User:1');"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Query error.",
                    e,
                    DeleteOrResetStatementService
                )
        
        statement_owner = query_result[0]['result'][0]['user_owner']
        
        if statement_owner == 'User:1':
            try: 
                # reset the array to only one element with the first element
                query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT * FROM "
                    f"Statement WHERE "
                    f"id = 'Statement:{statement_id}'"
                    f") SET text = ['{query_result[0]['result'][0]['text'][0]}'];"
                )

                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e: 
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Deletion 1 for Scanlytics Statement didnt work.",
                    e,
                    DeleteOrResetStatementService
                )

            try: 
                try:
                    query_result = await db.query(
                        f"RETURN array::len(("
                        f"SELECT text "
                        f"FROM Statement "
                        f"WHERE id = 'Statement:{statement_id}'"
                        f")[0]['text']);"
                    )

                    DatabaseErrorHelper(query_result, error_stack)

                    len_text_array = query_result[0]['result']

                except Exception as e:
                    error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Deletion 2 for Scanlytics Statement didnt work.",
                        e,
                        DeleteOrResetStatementService
                    )

                if len_text_array == 1:
                    return JSONResponse(
                        status_code=200, 
                        content=[
                            {
                                "message": f"Statement '{statement_id}' was set back to original state."
                            }, 
                            ReturnAccessTokenHelper(current_user_id, error_stack)
                            ]
                        )
                
                else:
                    error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "len_text_array is not 1.",
                        "None",
                        DeleteOrResetStatementService
                    )

            except Exception as e:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Determining successful deletion didnt work.",
                        e,
                        DeleteOrResetStatementService
                    )    
        else: 
            try: 
                query_result = await db.query(
                    f"DELETE ("
                    f"SELECT * FROM "
                    f"Statement WHERE "
                    f"id = Statement:{statement_id} "
                    f"AND user_owner = '{current_user_id}');"
                )

                DatabaseErrorHelper(query_result, error_stack)
                
        
            except Exception as e: 
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Deletion query didnt work.",
                        e,
                        DeleteOrResetStatementService
                    )  
                

            try:
                query_result = await db.query(
                    f"SELECT * FROM Statement "
                    f"WHERE id = Statement:{statement_id};"
                )

                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Determining successful deletion didnt work.",
                        e,
                        DeleteOrResetStatementService
                    )
                
            try:
                if not query_result[0]['result']:
                    return JSONResponse(
                        status_code=200, 
                        content=[
                            {
                                "message": f"Statement '{statement_id}' deletion was successful."
                            }, 
                            ReturnAccessTokenHelper(current_user_id, error_stack)
                            ]
                        )

            except Exception as e:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Returning JSON Response for successful deletion didnt work.",
                        e,
                        DeleteOrResetStatementService
                    )


                
    except Exception as e:
        ExceptionHelper(UpdateStatementService, e, error_stack)

