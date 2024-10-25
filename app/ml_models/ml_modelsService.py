import os
import boto3

from fastapi import HTTPException, status
from botocore.exceptions import ClientError
from fastapi.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenService
from app.db.database import DatabaseResultService
from functools import lru_cache

@lru_cache()
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('S3_SECRET_KEY')
    )

s3_client = get_s3_client()

async def RetrieveModelService(model_name, current_user_id, db):
    model_name_str = model_name.model_name if hasattr(model_name, 'model_name') else model_name
    model_name_str = model_name_str.replace('.onnx', '')
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': os.getenv('S3_BUCKET_NAME'),
                'Key': f'{model_name_str}.onnx'
            },
            ExpiresIn=3600
        )
        return JSONResponse(content={"url": url})
    except ClientError as e:
        raise HTTPException(status_code=404, detail="Model not found")
