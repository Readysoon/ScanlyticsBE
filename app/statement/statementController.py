from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.auth.authService import GetCurrentUserIDHelper
from app.db.database import get_db

from app.statement.statementService import write_statement_service, initialize_statements_service, search_statements_service, get_statement_service, get_all_statements_service, update_statement_service, delete_or_reset_statement_service
from app.statement.statementSchema import Statement


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
        statement_in: Statement, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await write_statement_service(
            statement_in,
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
@router.get("/search")
async def search_statements(
        search_in: Statement,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await search_statements_service(
            search_in,
            current_user_id,
            db
        )

'''gets a single statement'''
@router.get("/{statement_id}")
async def get_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await get_statement_service(
            statement_id,
            current_user_id,
            db
        )

'''gets all users statements'''
@router.get("/")
async def get_all_statement(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await get_all_statements_service(
            current_user_id,
            db
        )

'''updating adding a new text to the array or changing the other parameters'''
@router.patch("/{statement_id}")
async def update_statement(
        statement_id: str,
        statement_in: Statement, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await update_statement_service(
            statement_id,
            statement_in,
            current_user_id,
            db
        )

'''delete added array<string> but you cannot delete Scanlytics statements (because theyre anyways not yours)'''
@router.delete("/{statement_id}")
async def delete_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await delete_or_reset_statement_service(
            statement_id,
            current_user_id,
            db
        )

