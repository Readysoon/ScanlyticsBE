import os

from fastapi import HTTPException, status

from scanlyticsbe.app.db.database import DatabaseResultService
from scanlyticsbe.app.auth.authService import ReturnAccessTokenService

from scanlyticsbe.app.statement.statementSchema import Statement

# imports for initialize_statements
from surrealdb import Surreal
from scanlyticsbe.app.db.database import get_db
from fastapi import APIRouter, Depends



#             "DEFINE TABLE Statement SCHEMAFULL;",
#             "DEFINE FIELD text ON Statement TYPE string;",
#             "DEFINE FIELD body_part ON Statement TYPE string;",
#             "DEFINE FIELD medical_condition ON Statement TYPE string;",
#             "DEFINE FIELD modality ON Statement TYPE string;",
#             "DEFINE FIELD section ON Statement TYPE string;",
#             "DEFINE FIELD created_at ON Statement TYPE datetime DEFAULT time::now();",
#             "DEFINE FIELD updated_at ON Statement TYPE datetime DEFAULT time::now() VALUE time::now();",
#             "DEFINE FIELD user_owner ON Statement TYPE record(User);",


async def write_statement(statementin, current_user_id, db):
    try:
        # this and the if statement afterwards is for the seed function below to not create duplicates
        try:
            query_result = await db.query(
                f"SELECT * FROM Statement "
                f"WHERE text = '{statementin.text}'"
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Select Statements didnt work: {e}")
        
        if not query_result[0]['result']:
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
            
            return ReturnAccessTokenService(current_user_id), query_result[0]['result'][0]
                
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"write_statement: {e}")
    

# Path to the reportTemplates directory
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'reportTemplates')

async def initialize_statements(
        db: Surreal = Depends(get_db)
    ):
    print("initialize_statements:")
    for file_name in os.listdir(TEMPLATES_DIR):
        print(f"filename: {file_name}")
        if file_name.endswith('.txt'):
            file_path = os.path.join(TEMPLATES_DIR, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:

                base_name, _ = os.path.splitext(file_name)  # Split the file name from its extension

                file_name_parts = base_name.split() # split Röntgen and the body_part

                content = file.read()
                words = content.split()  # Split the content into words

                Statement.text = ""
                Statement.body_part = file_name_parts[1]
                Statement.medical_condition = "sick"
                Statement.modality = file_name_parts[0]
                Statement.section = ""

                # if file_name_parts[0] == "Befund":
                #     einleitung_text = []
                #     for word in words:
                #         einleitung_text += word
                #     break

                text = []
                for word in words:
                    if word in ["__Indikation__", "__Technik__", "__Klinik__", "__Vergleich__", "__Befund__", "__Beurteilung__"]:
                        if text:  # Only assign if text is not empty
                            Statement.text = " ".join(text)  # Join the words in text to form a string
                            text = []  # Reset text for the next section
                        Statement.section = word  # Set the current section to the keyword
                    else:
                        text.append(word)  # Append word to text

                await write_statement(Statement, "User:1", db)

                # print(Statement.text)
                # print(Statement.body_part)
                # print(Statement.medical_condition)
                # print(Statement.modality)
                # print(Statement.section)




                
# Example usage
if __name__ == "__main__":
    initialize_statements()




