import os

from starlette.responses import JSONResponse

from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType


MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = os.getenv("MAIL_PORT")
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS")
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS")
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS")
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS")


# outsource to .env
conf = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD = MAIL_PASSWORD,
    MAIL_FROM = MAIL_FROM,
    MAIL_PORT = MAIL_PORT,
    MAIL_SERVER = MAIL_SERVER,
    MAIL_FROM_NAME= MAIL_FROM_NAME,
    MAIL_STARTTLS = MAIL_STARTTLS,
    MAIL_SSL_TLS = MAIL_SSL_TLS,
    USE_CREDENTIALS = USE_CREDENTIALS,
    VALIDATE_CERTS = VALIDATE_CERTS
)

async def simple_send_service(email):
    try:
        html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """

        email_list = []

        email_list.append(email)

        message = MessageSchema(
            subject="Fastapi-Mail module",
            recipients=email_list,# email.dict().get("email"), #use this if you want to send an email in json format {"email": ["fpb56915@dcobe.com"]}
            body=html,
            subtype=MessageType.html)

        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Sending the verification mail didnt work: {e}")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
