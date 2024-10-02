from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.auth.authService import GetCurrentUserIDService
from scanlyticsbe.app.db.database import get_db

from scanlyticsbe.app.statement.statementService import write_statement
from scanlyticsbe.app.statement.statementSchema import Statement


'''A user can only change an existing statement'''
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
    return await write_statement(
            statementin,
            current_user_id,
            db
        )