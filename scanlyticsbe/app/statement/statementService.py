import os

from fastapi import HTTPException, status

from scanlyticsbe.app.db.database import DatabaseResultService
from scanlyticsbe.app.auth.authService import ReturnAccessTokenService

from scanlyticsbe.app.statement.statementSchema import Statement

async def write_statement_service(statementin, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"CREATE Statement "
                f"SET text += '{statementin.text}', "
                f"body_part = '{statementin.body_part}', "
                f"medical_condition = '{statementin.medical_condition}', "
                f"modality = '{statementin.modality}', "
                f"section = '{statementin.section}', "
                f"user_owner = '{current_user_id}';"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        '''differentiate between a statement writen by the user and by the initialization'''
        if current_user_id != "User:1":
            return ReturnAccessTokenService(current_user_id), query_result[0]['result'][0]
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"write_statement_service: {e}")
    

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'reportTemplates')

async def initialize_statements_service(db):
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
                            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Select Statements didnt work: {e}")
                        
                        if not query_result[0]['result'] and statement_instance.section:
                            await write_statement_service(statement_instance, "User:1", db)


async def get_last_statement_text_element(statement_id, db):
    try:
        query_result = await db.query(
            f"RETURN array::len(("
            f"SELECT text FROM "
            f"Statement WHERE "
            f"id = '{statement_id}'"
            f")[0]['text']);"
        )

        DatabaseResultService(query_result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"get_last_statement_text_element: {e}")
    
    last_list_element = query_result[0]['result'] - 1
    
    return last_list_element

'''to be adapted to return last text elements'''
async def search_statements_service(searchin, current_user_id, db):
    try:
        try:
            section = searchin.section
            body_part = searchin.body_part
            medical_condition = searchin.medical_condition
            modality = searchin.modality
            text = searchin.text
            search_string = ""

            # elongate the update_string
            if text:
                '''Do the sql/surreal text search magic here (instead of just this simple version)'''
                search_string += f"text = '{text}' AND "
            if section:
                search_string += f"section = '{section}' AND "
            if body_part:
                search_string += f"body_part = '{body_part}' AND "
            if medical_condition:
                search_string += f"medical_condition = '{medical_condition}' AND "
            if modality:
                search_string += f"modality = '{modality}' AND "
            
            search_string = search_string[:-5]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Search-string creation failed: {e}")
               
        try:
            query_result = await db.query(
                f"SELECT id FROM Statement "
                f"WHERE {search_string} AND "
                f"(user_owner = '{current_user_id}' OR "
                f"user_owner = 'User:1');"
            )
            print(search_string)
            print(current_user_id)
            print(query_result)
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")

        last_element_number = await get_last_statement_text_element(query_result[0]['result'][0]['id'], db)

        try: 
            query_result = await db.query(
                f"SELECT text[{last_element_number}],* "
                f"FROM Statement WHERE "
                f"id = '{query_result[0]['result'][0]['id']}';"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Second Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']

        return ReturnAccessTokenService(current_user_id), result_without_status
        
        # add or remove '[0]' for multiple results
        return ReturnAccessTokenService(current_user_id), query_result[0]['result']
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"search_statements_service: {e}")
    
'''works with last array elements'''
async def get_statement_service(statement_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE id = 'Statement:{statement_id}' "
                f"AND (user_owner = {current_user_id} "
                f"OR user_owner = 'User:1');"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"First Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this statement.")
        
        last_element_number = await get_last_statement_text_element(query_result[0]['result'][0]['id'], db)

        try: 
            query_result = await db.query(
                f"SELECT text[{last_element_number}],* "
                f"FROM Statement WHERE "
                f"id = '{query_result[0]['result'][0]['id']}';"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Second Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']
  
        return ReturnAccessTokenService(current_user_id), result_without_status
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"get_statement_service: {e}")  
    
'''works with last array elements'''
async def get_all_statements_service(current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE user_owner = '{current_user_id}';"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this user.")
        
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
                DatabaseResultService(query_result)
                
                result_list.append(query_result[0]['result'][0])
    
            except Exception as e: 
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
  
        return ReturnAccessTokenService(current_user_id), result_list
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"get_statement_service: {e}")  

    
'''works with list functionality'''
async def update_statement_service(statement_id, statementin, current_user_id, db):
    try:
        try:
            section = statementin.section
            body_part = statementin.body_part
            medical_condition = statementin.medical_condition
            modality = statementin.modality
            text = statementin.text
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")
        
        try:
            # and finally put everything together and send it
            query_result = await db.query(
                f"UPDATE ("
                f"SELECT * FROM Statement WHERE "
                f"id = 'Statement:{statement_id}' "
                f"AND user_owner = '{current_user_id}'"
                f") {set_string};"
                )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"First Database operation didnt work: {e}")
    
        last_element_number = await get_last_statement_text_element(query_result[0]['result'][0]['id'], db)

        try: 
            query_result = await db.query(
                f"SELECT text[{last_element_number}],* "
                f"FROM Statement WHERE "
                f"id = '{query_result[0]['result'][0]['id']}';"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Second Database operation didnt work. {e}")
        
        result_without_status = query_result[0]['result']
  
        return ReturnAccessTokenService(current_user_id), result_without_status
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"update_statement_service: {e}")

'''implement checking if deletion worked'''
'''implement removing all additional texts in arrays when deleting a scanlytics statement'''
async def delete_or_reset_statement_service(statement_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"DELETE ("
                f"SELECT * FROM "
                f"Statement WHERE "
                f"id = Statement:{statement_id} "
                f"AND user_owner = '{current_user_id}');"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        '''how to return access token here?'''
        if query_result[0] == '':
            return HTTPException(status_code=status.HTTP_200_OK, detail="Patient was deleted successfully.")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"delete_or_reset_statement_service: {e}")  

