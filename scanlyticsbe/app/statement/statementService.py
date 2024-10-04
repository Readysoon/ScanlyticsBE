import os

from fastapi import HTTPException, status

from scanlyticsbe.app.db.database import DatabaseResultService
from scanlyticsbe.app.auth.authService import ReturnAccessTokenService

from scanlyticsbe.app.statement.statementSchema import Statement

async def write_statement(statementin, current_user_id, db):
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
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Create Statements didnt work: {e}")
        
        # return ReturnAccessTokenService(current_user_id), query_result[0]['result'][0]
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"write_statement: {e}")
    

# Path to the reportTemplates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'reportTemplates')


# async def initialize_statements(
async def initialize_statements(db):
    print("initialize_statements:")
    for file_name in os.listdir(TEMPLATES_DIR):
        print(f"filename: {file_name}")
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
                            await write_statement(statement_instance, "User:1", db)


