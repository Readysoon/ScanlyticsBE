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
APP_URL = os.getenv("APP_URL")


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

async def email_verification_service(email, token, first_name):
    try:
        html = f"""
        <p>Hi {first_name}, this is a test mail. Thanks for using Fastapi-mail!</p>
        <p>Please click the button below to verify your email:</p>
        <table width="100%" cellspacing="0" cellpadding="0">
            <tr>
                <td>
                    <table cellspacing="0" cellpadding="0">
                        <tr>
                            <td style="border-radius: 2px;" bgcolor="#007BFF">
                                <a href="{APP_URL}/auth/verify/{token}" target="_blank" style="padding: 8px 12px; border: 1px solid #007BFF;border-radius: 2px;font-family: Helvetica, Arial, sans-serif;font-size: 14px; color: #ffffff;text-decoration: none;font-weight:bold;display: inline-block;">
                                    Verify Email
                                </a>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """

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
