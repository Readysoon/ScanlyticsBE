from fastapi import APIRouter

from scanlyticsbe.app.email.emailSchema import EmailSchema
from scanlyticsbe.app.email.emailService import email_verification_service


router = APIRouter(
        prefix="/email",
        tags=["email"],
    )


@router.post("/verify")
async def simple_send(
    email: EmailSchema
    ):
    return await email_verification_service(email)