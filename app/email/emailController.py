from fastapi import APIRouter

from .emailSchema import EmailSchema
from .emailService import EmailVerificationService

from app.error.errorHelper import ErrorStack, RateLimit

router = APIRouter(
        prefix="/email",
        tags=["email"],
    )

'''so far used only to test the service'''
@router.post("/verify", dependencies=[RateLimit.limiter()])
async def send_verification_mail(
    email: EmailSchema
    ):
    error_stack = ErrorStack()
    return await EmailVerificationService(
            email,
            error_stack
        )
