from fastapi import APIRouter, Depends
from surrealdb import Surreal

from .statementService import CreateStatementService, InitializeStatementsService, SearchStatementService, GetStatementByIDService, GetAllStatementsByUserService, UpdateStatementService, DeleteOrResetStatementService
from .statementSchema import Statement

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


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
    error_stack = ErrorStack()
    return await CreateStatementService(
            statement_in,
            current_user_id,
            db,
            error_stack
        )


@router.post("/initialize")
async def initialize_statements(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await InitializeStatementsService(
            current_user_id,
            db,
            error_stack
        )


'''gets scanlytics statements by categories and user statements by categories'''
@router.get("/search")
async def search_statements(
        search_in: Statement,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await SearchStatementService(
            search_in,
            current_user_id,
            db,
            error_stack
        )


'''gets a single statement'''
@router.get("/{statement_id}")
async def get_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetStatementByIDService(
            statement_id,
            current_user_id,
            db,
            error_stack
        )


'''gets all users statements'''
@router.get("/")
async def get_all_statement(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetAllStatementsByUserService(
            current_user_id,
            db,
            error_stack
        )


'''updating adding a new text to the array or changing the other parameters'''
@router.patch("/{statement_id}")
async def update_statement(
        statement_id: str,
        statement_in: Statement, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UpdateStatementService(
            statement_id,
            statement_in,
            current_user_id,
            db,
            error_stack
        )


'''delete added array<string> but you cannot delete Scanlytics statements (because theyre anyways not yours)'''
@router.delete("/{statement_id}")
async def delete_statement(
        statement_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await DeleteOrResetStatementService(
            statement_id,
            current_user_id,
            db,
            error_stack
        )

