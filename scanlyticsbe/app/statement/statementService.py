import os

from fastapi import HTTPException, status

from scanlyticsbe.app.db.database import DatabaseResultService
from scanlyticsbe.app.auth.authService import ReturnAccessTokenService

from scanlyticsbe.app.statement.statementSchema import Statement

'''write_statement_service, initialize_statements_service, get_statements_by_categories_service, '''
'''get_statement_service, update_statement_service, delete_or_reset_statement_service'''

async def write_statement_service(statementin, current_user_id, db):
    try:
        try:
            query_result = await db.query(
                f"CREATE Statement "
                f"SET text = '{statementin.text}', "
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
    

# Path to the reportTemplates directory
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

'''TO BE TESTED'''
async def search_statements_service(searchin, current_user_id, db):
    try:
        try:
            section = searchin.patient_name
            body_part = searchin.date_of_birth
            medical_condition = searchin.gender
            modality = searchin.contact_number
            text = searchin.text
            search_string = ""

            # elongate the update_string
            if text:
                '''Do the sql/surreal text search magic here (instead of just this simple version)'''
                search_string += f"text = '{text}', "
            if section:
                search_string += f"section = '{section}', "
            if body_part:
                search_string += f"body_part = '{body_part}', "
            if medical_condition:
                search_string += f"medical_condition = '{medical_condition}', "
            if modality:
                search_string += f"modality = '{modality}', "
            
            search_string = search_string[:-2]

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Search-string creation failed: {e}")
        
        try:
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE {search_string} AND "
                f"user_owner = '{current_user_id}' OR "
                f"user_owner = 'User:1';"
            )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        return ReturnAccessTokenService(current_user_id), query_result[0]['result'][0]
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"search_statements_service: {e}")
    
'''TO BE TESTED'''
async def get_statement_service(statement_id, current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE id = 'Statement:{statement_id}' "
                f"AND user_owner = {current_user_id} "
                f"OR user_owner = 'User:1';"
            )
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        if not query_result[0]['result']:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No record was found for this patient.")
        
        result_without_status = query_result[0]['result'][0]
  
        return ReturnAccessTokenService(current_user_id), result_without_status
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Looking up Patient didnt work: {e}")  
    
'''TO BE TESTED'''
async def update_statement_service(statement_id, statementin, current_user_id, db):
    try:
        try:
            section = statementin.patient_name
            body_part = statementin.date_of_birth
            medical_condition = statementin.gender
            modality = statementin.contact_number
            text = statementin.text
            set_string = "SET "

            # elongate the update_string
            if text:
                set_string += f"text = '{text}', "
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
                    f"SELECT * FROM Statement "
                    f"WHERE id = '{statement_id}' "
                    f"AND user_owner = {current_user_id} "
                    f") {set_string};"
                )

            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        return ReturnAccessTokenService(current_user_id), query_result[0]['result'][0]
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"search_statements_service: {e}")

    
async def delete_or_reset_statement_service(statement_id, current_user_id, db):
    

