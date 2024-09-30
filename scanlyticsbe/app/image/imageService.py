import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from fastapi import HTTPException, status

from scanlyticsbe.app.auth.authService import ReturnAccessTokenService
from scanlyticsbe.app.db.database import DatabaseResultHandlerService


# Load .env file from a specific path
load_dotenv()

# AWS S3 Configuration
S3_BUCKET = "hanswurstbucket"  # Replace with your bucket name
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")  # Set your AWS access key in environment variables
S3_SECRET_KEY = os.getenv("AWS_SECRET_KEY")  # Set your AWS secret key in environment variables
S3_REGION = "eu-north-1"  # Replace with your region, e.g., 'us-west-2'

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

async def UploadImageService(file, patient_id, current_user_id, db):   
    try:
        file.filename = file.filename.replace(" ", "_")

        file_type = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'unknown'

        # Upload the file to S3
        s3_client.upload_fileobj(file.file, S3_BUCKET, file.filename)

        # Construct the S3 URL for the uploaded file
        s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

        # Save image metadata in SurrealDB
        try:
            query_result = await db.query(
                f"CREATE Image "
                f"SET name = '{file.filename}', "
                f"path = '{s3_url}', "
                f"body_type = 'arm', "
                f"modal_type = 'mri', "
                f"file_type = '{file_type}', "
                f"patient = 'Patient:{patient_id}', "
                f"user = '{current_user_id}'"
            )

            DatabaseResultHandlerService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation failed: {e}")

        return ReturnAccessTokenService(query_result), query_result[0]['result']

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="Credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def GetImagesByPatient():
    print('empty')