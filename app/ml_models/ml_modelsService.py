import os
import boto3
from functools import lru_cache

from fastapi import status
from botocore.exceptions import ClientError
from fastapi.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper

from app.error.errorHelper import ExceptionHelper


@lru_cache()
def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
        aws_secret_access_key=os.getenv('S3_SECRET_KEY')
    )

s3_client = get_s3_client()

async def RetrieveModelService(model_name, current_user_id, db, error_stack):
    try:
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
            error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    "Model not found.",
                    e,
                    RetrieveModelService
                )
            
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Model found."
                    }, 
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
           
    except Exception as e:
        ExceptionHelper(RetrieveModelService, e, error_stack)

