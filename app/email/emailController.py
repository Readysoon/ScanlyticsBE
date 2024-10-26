from fastapi import APIRouter

from app.email.emailSchema import EmailSchema
from app.email.emailService import EmailVerificationService


router = APIRouter(
        prefix="/email",
        tags=["email"],
    )

'''used only to test the service'''
@router.post("/verify")
async def simple_send(
    email: EmailSchema
    ):
    return await EmailVerificationService(email)