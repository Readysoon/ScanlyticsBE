from fastapi import status

from app.auth.authService import ReturnAccessTokenHelper

from app.statement.statementSchema import Statement
from app.statement.statementService import SearchStatementService

from app.error.errorHelper import ExceptionHelper

'''"Analyzes" an image and returns a set of categories which then are used in get_statements_by category to pregenerate a report"'''

async def ClassifyService(image_array, current_user_id, db, error_stack):
    try:
        # random_body_part = random.choice(['Fuß', 'LWS', 'Thorax', 'Thorax', 'Hand', 'Hüfte', 'Ellbogen', 'Schulter'])
        # random_section = random.choice(['__Beurteilung__', '__Befund__', '__Vergleich__', '__Klinik__', '__Technik__', '__Indikation__'])

        searchin = Statement

        searchin.text = ''
        searchin.body_part = 'LWS'
        searchin.medical_condition = 'sick'
        searchin.modality = 'Röntgen'
        searchin.section = ''

        try:
            results_SearchStatementService = await SearchStatementService(searchin, current_user_id, db, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "SearchStatementService.",
                e,
                ClassifyService
            )
        try: 
            statements = results_SearchStatementService[1]

            statement_id_list = []

            for statement in statements:
                statement_id = statement['id'], statement['text']
                statement_id_list.append(statement_id)

            return ReturnAccessTokenHelper(current_user_id, error_stack), statement_id_list
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Processing SearchStatementService Result caused an error.",
                e,
                ClassifyService
            )
    
    except Exception as e:
        ExceptionHelper(ClassifyService, error_stack, e)

