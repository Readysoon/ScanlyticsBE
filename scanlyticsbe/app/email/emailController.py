from fastapi import APIRouter

from scanlyticsbe.app.email.emailSchema import EmailSchema
from scanlyticsbe.app.email.emailService import simple_send_service


router = APIRouter(
        prefix="/email",
        tags=["email"],
    )


@router.post("/verify")
async def simple_send(
    email: EmailSchema
    ):
    return await simple_send_service(email)