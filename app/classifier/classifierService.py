from app.auth.authService import ReturnAccessTokenService

from app.statement.statementSchema import Statement
from app.statement.statementService import search_statements_service



'''"Analyzes" an image and returns a set of categories which then are used in get_statements_by category to pregenerate a report"'''

async def classify_service(image_array, current_user_id, db):

    # random_body_part = random.choice(['Fuß', 'LWS', 'Thorax', 'Thorax', 'Hand', 'Hüfte', 'Ellbogen', 'Schulter'])
    # random_section = random.choice(['__Beurteilung__', '__Befund__', '__Vergleich__', '__Klinik__', '__Technik__', '__Indikation__'])

    searchin = Statement

    searchin.text = ''
    searchin.body_part = 'LWS'
    searchin.medical_condition = 'sick'
    searchin.modality = 'Röntgen'
    searchin.section = ''

    results_search_statements_service = await search_statements_service(searchin, current_user_id, db)

    statements = results_search_statements_service[1]

    statement_id_list = []

    for statement in statements:
        statement_id = statement['id'], statement['text']
        statement_id_list.append(statement_id)

    return ReturnAccessTokenService(current_user_id), statement_id_list
