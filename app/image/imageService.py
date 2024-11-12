import os
import boto3
from typing import Set
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv
from fastapi import status
from starlette.responses import JSONResponse

from .imageHelper import GetImagesByPatientHelper, DeleteImageByIDHelper

from app.auth.authHelper import ReturnAccessTokenHelper
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

MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB in bytes
ALLOWED_FILE_TYPES: Set[str] = {
    'jpeg',
    'jpg',
    'png',
    'gif',
    'webp'
}

'''error: patient not found'''
async def UploadImageService(file, patient_id, current_user_id, db, error_stack):   
    try:
        try:
            # first verify patient is users
            try:
                query_result = await db.query(
                """
                SELECT * 
                FROM Patient 
                WHERE id = $patient_id 
                AND (
                    SELECT * 
                    FROM Treated_By 
                    WHERE out = $user_id
                );
                """,
                {
                    "patient_id": f"Patient:{patient_id}",
                    "user_id": current_user_id
                }
                )
 
                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Select Patient Query error: {query_result}",
                    e,
                    UploadImageService
                ) 

            if not query_result[0]['result']:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"No Patient was found for this id: '{patient_id}'. Maybe check for Typo?",
                    "None",
                    UploadImageService
                ) 
            # end of patient ownership verification part - maybe own function?

            try:
                file.filename = file.filename.replace(" ", "_")

                file_type = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else 'unknown'

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "File name/type handling error.",
                    e,
                    UploadImageService
                )

            if file.size > MAX_FILE_SIZE:
                error_stack.add_error(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    "File size exceeds maximum limit",
                    "None",
                    UploadImageService
                )

            if file_type not in ALLOWED_FILE_TYPES:
                error_stack.add_error(
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    f"File type not supported; file type: {file_type}",
                    "None",
                    UploadImageService
                )

            try:
                # Upload the file to S3
                s3_client.upload_fileobj(file.file, S3_BUCKET, file.filename)

                # Construct the S3 URL for the uploaded file
                s3_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    "S3 uploading/URL construction error.",
                    e,
                    UploadImageService
                )

            # Save image metadata in SurrealDB
            try:
                query_result = await db.query(
                    """
                    CREATE Image SET 
                        name = $filename,
                        path = $url,
                        body_part = $body_part,
                        modality = $modality,
                        file_type = $file_type,
                        patient = $patient_id,
                        user = $user_id
                    """,
                    {
                        "filename": file.filename,
                        "url": s3_url,
                        "body_part": "arm",
                        "modality": "mri",
                        "file_type": file_type,
                        "patient_id": f"Patient:{patient_id}",
                        "user_id": current_user_id
                    }
                )

                DatabaseErrorHelper(query_result, error_stack)

                image_data = query_result[0]['result'][0]

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    UploadImageService
                ) 

            return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Image '{file.filename}' has been uploaded."
                    }, 
                    image_data,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

        except NoCredentialsError as e:
            error_stack.add_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "Credentials not available.",
                    e,
                    UploadImageService
                ) 
    
    except Exception as e:
        ExceptionHelper(UploadImageService, e, error_stack)
    
'''
# Suggested
status.HTTP_404_NOT_FOUND  # when no images found for patient - check
status.HTTP_403_FORBIDDEN  # when user doesn't have access to patient's images -check
status.HTTP_200_OK  # for successful retrieval (add this) - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check
'''
async def GetImagesByPatientService(patient_id, current_user_id, db, error_stack):
    try:

        image_list = await GetImagesByPatientHelper(patient_id, current_user_id, db, error_stack)

        image_count = 0

        if not image_list:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Patient has no images",
                    e,
                    GetImagesByPatientHelper
                ) 

        for image in image_list:
            image_count += 1
            
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched {image_count} image(s) for patient '{patient_id}'."
                    }, 
                    image_list,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

    except Exception as e:
        ExceptionHelper(GetImagesByPatientService, e, error_stack)


'''
# Suggested:
status.HTTP_404_NOT_FOUND  # when image not found - check
status.HTTP_403_FORBIDDEN  # when user doesn't have access to the image - check
status.HTTP_200_OK  # for successful retrieval (add this) - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check 
'''
async def GetImageByIDService(image_id, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                """
                SELECT * 
                FROM Image 
                WHERE id = $image_id;
                """,
                {
                    "image_id": f"Image:{image_id}"
                }
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query 1 error.",
                    e,
                    GetImageByIDService
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    f"No Image found for ID '{image_id}'.",
                    "None",
                    GetImageByIDService
                )
            
        try:
            query_result = await db.query(
                """
                SELECT * 
                FROM Image 
                WHERE user = $user_id 
                AND id = $image_id;
                """,
                {
                    "user_id": current_user_id,
                    "image_id": f"Image:{image_id}"
                }
            )

            DatabaseErrorHelper(query_result, error_stack)

            image_data = query_result[0]['result'][0]

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query 2 error.",
                    e,
                    GetImageByIDService
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    f"You are not authorized to view image '{image_id}'.",
                    "None",
                    GetImageByIDService
                )
        
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched image '{image_id}'."
                    }, 
                    image_data,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

    except Exception as e:
        ExceptionHelper(GetImageByIDService, e, error_stack)


'''
status.HTTP_200_OK  # for successful update - check
status.HTTP_404_NOT_FOUND  # when image not found - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to update  - check
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data - to be done in schema checking
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check
'''
async def UpdateImageService(image_in, image_id, current_user_id, db, error_stack):
        try:
            try:
                query_result = await db.query(
                    """
                    SELECT * 
                    FROM Image 
                    WHERE id = $image_id;
                    """,
                    {
                        "image_id": f"Image:{image_id}"
                    }
                )

                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Query 1 error.",
                        e,
                        GetImageByIDService
                    ) 
            
            if not query_result[0]['result']:
                error_stack.add_error(
                        status.HTTP_404_NOT_FOUND,
                        f"No Image found for ID '{image_id}'.",
                        "None",
                        GetImageByIDService
                    )
                
            try:
                query_result = await db.query(
                    """
                    SELECT * 
                    FROM Image 
                    WHERE user = $user_id 
                    AND id = $image_id;
                    """,
                    {
                        "user_id": current_user_id,
                        "image_id": f"Image:{image_id}"
                    }
                )

                DatabaseErrorHelper(query_result, error_stack)

            except Exception as e:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "Query 2 error.",
                        e,
                        GetImageByIDService
                    ) 
            
            if not query_result[0]['result']:
                error_stack.add_error(
                        status.HTTP_401_UNAUTHORIZED,
                        f"You are not authorized to view image '{image_id}'.",
                        "None",
                        GetImageByIDService
                    )

            try:
                set_parts = []
                update_params = {}

                if image_in.image_name:
                    set_parts.append("name = $image_name")
                    update_params["image_name"] = image_in.image_name

                if image_in.body_part:
                    set_parts.append("body_part = $body_part")
                    update_params["body_part"] = image_in.body_part

                if image_in.modality:
                    set_parts.append("modality = $modality")
                    update_params["modality"] = image_in.modality

                query_result = await db.query(
                    f"""
                    UPDATE Image 
                    SET {", ".join(set_parts)}
                    WHERE user = $user_id 
                    AND id = $image_id;
                    """,
                    {
                        "user_id": current_user_id,
                        "image_id": f"Image:{image_id}",
                        **update_params  
                    }
                )
                
                DatabaseErrorHelper(query_result, error_stack)
   
            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    UpdateImageService
                )

            return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Updated image '{image_id}'."
                    }, 
                    query_result[0]['result'],
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

        except Exception as e:
            ExceptionHelper(UpdateImageService, e, error_stack)
    

'''Delete it in the storage'''
'''
#Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion - check 
status.HTTP_404_NOT_FOUND  # when image not found - check 
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete - check 
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check 
'''
async def DeleteImageByIDService(image_id, current_user_id, db, error_stack):
    try:
        deleted = await DeleteImageByIDHelper(image_id, current_user_id, db, error_stack)
            
        if deleted == True:
            return JSONResponse(
                status_code=204,
                content=[
                    {
                        "message": f"Image deletion successfull."
                    }, 
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
    
    except Exception as e:
        ExceptionHelper(DeleteImageByIDService, e, error_stack)
