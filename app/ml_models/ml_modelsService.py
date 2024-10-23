from fastapi import HTTPException, status
from app.auth.authService import ReturnAccessTokenService
from app.db.database import DatabaseResultService
import boto3
from botocore.exceptions import ClientError
from fastapi.responses import JSONResponse
from pydantic import BaseSettings
from functools import lru_cache

class S3Settings(BaseSettings):
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET_NAME: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return S3Settings()

settings = get_settings()
s3_client = boto3.client(
    's3',
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY
)

async def GetModel(model_name, current_user_id, db):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': f'{model_name}.onnx'
            },
            ExpiresIn=3600
        )
        return JSONResponse(content={"url": url})
    except ClientError as e:
        raise HTTPException(status_code=404, detail="Model not found")
