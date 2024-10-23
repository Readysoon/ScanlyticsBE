from fastapi import HTTPException, status

from app.auth.authService import ReturnAccessTokenService
from app.db.database import DatabaseResultService


s3_client = boto3.client(
    's3',
    endpoint_url='YOUR_S3_ENDPOINT_URL',
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY'
)

async def GetModel(ml_model, current_user_id, db):
    # Check if the user has access to the model
    # Check if the model exists
    # Get the model from S3
    # Return the model download link
    pass