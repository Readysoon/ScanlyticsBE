from fastapi import APIRouter

from app.email.emailSchema import EmailSchema
from app.email.emailService import EmailVerificationService

from app.error.errorHelper import ErrorStack

router = APIRouter(
        prefix="/email",
        tags=["email"],
    )

'''so far used only to test the service'''
@router.post("/verify")
async def send_verification_mail(
    email: EmailSchema
    ):
    error_stack = ErrorStack()
    return await EmailVerificationService(
            email,
            error_stack
        )