from fastapi import status
from starlette.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper

from app.statement.statementSchema import Statement
from app.statement.statementHelper import SearchStatementHelper

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
            results_SearchStatementService = await SearchStatementHelper(searchin, current_user_id, db, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "SearchStatementHelper.",
                e,
                ClassifyService
            )
        try: 
            statements = results_SearchStatementService

            statement_id_list = []

            for statement in statements:
                statement_id = statement['id'], statement['text']
                statement_id_list.append(statement_id)
            
            return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Classified image(s)."
                    },
                    statement_id_list,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
        
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Processing SearchStatementService Result caused an error.",
                e,
                ClassifyService
            )
    
    except Exception as e:
        ExceptionHelper(ClassifyService, e, error_stack)

