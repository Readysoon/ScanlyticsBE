from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.auth.authService import GetCurrentUserIDService
from scanlyticsbe.app.db.database import get_db

from scanlyticsbe.app.statement.statementService import write_statement_service, initialize_statements_service, search_statements_service, get_statement_service, update_statement_service, delete_or_reset_statement_service
from scanlyticsbe.app.statement.statementSchema import Statement, StatementSearch


'''A user can only change an existing statement and add their statements to existing categories'''
'''Statements are used to create Reports'''
'''A Statement deletion equals setting back to default - which doesnt necessarely mean you should use the delete method'''
'''Statements are seeded on startup'''
'''For Report generation a random category and disease will be picked'''

router = APIRouter(
    prefix="/statement",
    tags=["statement"],
)

@router.post("/")
async def create_statement(
        statementin: Statement, 
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await write_statement_service(
            statementin,
            current_user_id,
            db
        )

@router.post("/initialize")
async def initialize_statements(
        db: Surreal = Depends(get_db)
    ):
    return await initialize_statements_service(
            db
        )

'''gets scanlytics statements by categories and user statements by categories'''
@router.get("/categories")
async def search_statements(
        searchin: Statement,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await search_statements_service(
            searchin,
            current_user_id,
            db
        )

'''gets a single statement'''
@router.get("/{statement_id}")
async def get_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await get_statement_service(
            statement_id,
            current_user_id,
            db
        )

'''updating is creating a new and connecting to the old'''
@router.patch("/{statement_id}")
async def update_statement(
        statement_id: str,
        statementin: Statement, 
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await update_statement_service(
            statement_id,
            statementin,
            current_user_id,
            db
        )

'''delete "updated" statements but you cannot delete Scanlytics statements (because theyre anyways not yours)'''
@router.delete("/{statement_id}")
async def delete_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDService),
        db: Surreal = Depends(get_db)
    ):
    return await delete_or_reset_statement_service(
            statement_id,
            current_user_id,
            db
        )

