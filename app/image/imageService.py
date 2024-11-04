import os
import boto3
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from fastapi import status
from starlette.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


# Load .env file from a specific path
load_dotenv()

S3_BUCKET = os.getenv("AWS_BUCKET_NAME") 
S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")  
S3_SECRET_KEY = os.getenv("AWS_SECRET_KEY")  
S3_REGION = os.getenv("AWS_REGION")  

s3_client = boto3.client(
    "s3",
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION,
)

'''status.HTTP_413_REQUEST_ENTITY_TOO_LARGE  # for files exceeding size limit (add this check)'''
'''status.HTTP_415_UNSUPPORTED_MEDIA_TYPE  # for invalid file types (add this check)'''
async def UploadImageService(file, patient_id, current_user_id, db, error_stack):   
    try:
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
                    f"body_part = 'arm', "
                    f"modality = 'mri', "
                    f"file_type = '{file_type}', "
                    f"patient = 'Patient:{patient_id}', "
                    f"user = '{current_user_id}'"
                )

                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    UploadImageService
                ) 

            return JSONResponse(status_code=200, content={"message": "Image has been uploaded"}), ReturnAccessTokenHelper(current_user_id, error_stack)

        except NoCredentialsError as e:
            error_stack.add_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "Credentials not available.",
                    e,
                    UploadImageService
                ) 
        
    except Exception as e:
        ExceptionHelper(UploadImageService, error_stack, e)
    
'''
# Suggested
status.HTTP_404_NOT_FOUND  # when no images found for patient
status.HTTP_403_FORBIDDEN  # when user doesn't have access to patient's images
status.HTTP_200_OK  # for successful retrieval (add this)
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetImagesByPatient(patient_id, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM Image WHERE "
                f"user = '{current_user_id}' "
                f"AND patient = 'Patient:{patient_id}';"
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetImagesByPatient
                ) 
        
        return ReturnAccessTokenHelper(current_user_id, error_stack), query_result[0]['result']

    except Exception as e:
        ExceptionHelper(GetImagesByPatient, error_stack, e)

'''
# Suggested:
status.HTTP_404_NOT_FOUND  # when image not found
status.HTTP_403_FORBIDDEN  # when user doesn't have access to the image
status.HTTP_200_OK  # for successful retrieval (add this)
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetImageByID(image_id, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM Image WHERE "
                f"user = '{current_user_id}' "
                f"AND id = 'Image:{image_id}';"
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetImageByID
                ) 
        
        return ReturnAccessTokenHelper(current_user_id, error_stack), query_result[0]['result'][0]

    except Exception as e:
        ExceptionHelper(GetImageByID, error_stack, e)
    

'''
#Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when image not found
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeleteImageByID(image_id, current_user_id, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                    f"DELETE Image WHERE "
                    f"user = '{current_user_id}' "
                    f"AND id = 'Image:{image_id}';"
                )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    DeleteImageByID
                ) 
        
        if query_result[0] == '':
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Image was deleted successfully.",
                    "None",
                    DeleteImageByID
                ) 
    
    except Exception as e:
        ExceptionHelper(DeleteImageByID, error_stack, e)
    
'''
status.HTTP_200_OK  # for successful update
status.HTTP_404_NOT_FOUND  # when image not found
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to update
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def UpdateImageService(image_in, image_id, current_user_id, db, error_stack):
        try:
            try:
                image_name = image_in.image_name
                body_part = image_in.body_part
                modality = image_in.modality
                set_string = "SET "

                # elongate the update_string
                if image_name:
                    set_string += f"name = '{image_name}', "
                if body_part:
                    set_string += f"body_part = '{body_part}', "
                if modality:
                    set_string += f"modality = '{modality}', "
                
                set_string = set_string[:-2]

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Set-string creation failed.",
                    e,
                    DeleteImageByID
                ) 

            try: 
                # and finally put everything together and send it
                query_result = await db.query(
                    f"Update Image "
                    f"{set_string} WHERE "
                    f"user = '{current_user_id}' "
                    f"AND id = 'Image:{image_id}' "
                    f";"
                )
                
                DatabaseErrorHelper(query_result, error_stack)
   
            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    DeleteImageByID
                )
            
            return ReturnAccessTokenHelper(current_user_id, error_stack)

        except Exception as e:
            ExceptionHelper(UpdateImageService, error_stack, e)
