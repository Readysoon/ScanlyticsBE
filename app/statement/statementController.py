from fastapi import APIRouter, Depends, Path
from surrealdb import Surreal
from typing import Annotated

from .statementService import CreateStatementService, InitializeStatementsService, SearchStatementService, GetStatementByIDService, GetAllStatementsByUserService, UpdateStatementService, DeleteOrResetStatementService
from .statementSchema import Statement

from app.error.errorHelper import ErrorStack, RateLimit
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

@router.post("/", dependencies=[RateLimit.limiter()])
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


@router.post("/initialize", dependencies=[RateLimit.limiter()])
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
@router.get("/search", dependencies=[RateLimit.limiter()])
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
@router.get("/{statement_id}", dependencies=[RateLimit.limiter()])
async def get_statement(
        statement_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Statement ID must be 20 characters long and contain only alphanumeric characters"
                )],
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
@router.get("/", dependencies=[RateLimit.limiter()])
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
@router.patch("/{statement_id}", dependencies=[RateLimit.limiter()])
async def update_statement(
        statement_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Statement ID must be 20 characters long and contain only alphanumeric characters"
                )],
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
@router.delete("/{statement_id}", dependencies=[RateLimit.limiter()])
async def delete_statement(
        statement_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Statement ID must be 20 characters long and contain only alphanumeric characters"
                )],
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

