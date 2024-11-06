import os

from starlette.responses import JSONResponse
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from app.error.errorHelper import ExceptionHelper


MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Convert to integer
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS") == "True"  # Convert to boolean
MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS") == "True"  # Convert to boolean
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS") == "True"  # Convert to boolean
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS") == "True"  # Convert to boolean
APP_URL = os.getenv("APP_URL")

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

async def EmailVerificationService(email, token, first_name, error_stack):
    try:
        html = f"""
        <p>Hi {first_name},</p>
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

        return JSONResponse(
            status_code=200, 
            content=[
                {
                    "message": f"Email has been sent to {email}."
                }
                ]
            )
    
    except Exception as e:
        ExceptionHelper(EmailVerificationService, e, error_stack)
