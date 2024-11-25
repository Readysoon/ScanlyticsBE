## Website

Visit the website here: https://scanlyticsbe.fly.dev/

## Introduction

As an intern in various hospitals and countless talks with doctors it came to us that Julius and me had to do something to help them write their reports faster. Although there are already countless products analyzing medical images and speach-to-text solutions, they still dont seem to really convince them or came to something like an technological standstill. A new concept had to be developed and we came up with this FastAPI/Tauri WebApp whose core function are classifiers, which categorize medical images (later medical texts) and present statements (an idea of ours) out of which the doctor can choose to compose their report. The doctors can complete the out-of-statement-composed-report with their own added texts (in later version we also plan to incorporate speech-to-text to make this even faster) and change or add statements. Additionally for even better documentation the doctors are also able to create and manage notes. Proper patient management is of course also implemented.

## Installation

To install and run the project on your local machine, please follow these steps:

1. Clone the repository to your local machine by running the following command in your terminal:

      ```
      git clone https://github.com/Readysoon/ScanlyticsBE.git
      cd ScanlyticsBE
   
      ```

2. Install Poetry (if not already installed)

      ```
      # Windows (PowerShell)
      (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
      
      # macOS/Linux
      curl -sSL https://install.python-poetry.org | python3 -
      ```


2. Set up the virtual environment with poetry:
     
     To install the dependencies:

     ```
     poetry install
     ```

     To activate the virtual environment:

     ```
     poetry shell
     ```

     To exit the virtual environment (if necessary):

     ```
     exit
     ```

4. Make sure to have the Docker application up and ready (free of any containers/images with the same name)

5. Run Docker

     ```
     docker compose build && docker compose up
     
     ```

## Architecture/Security

View the architecture diagram here: https://miro.com/app/board/uXjVLYDG24o=/?share_link_id=101772163535

## API Endpoints

### Authentication Routes (/auth)
- POST `/auth/check_mail` - Check if email exists
- POST `/auth/orga_signup` - Register first user of an organization
- POST `/auth/user_signup` - Register a new user
- POST `/auth/login` - User login
- PATCH `/auth/password` - Update password
- POST `/auth/validate` - Validate user session
- GET `/auth/verify/{token}` - Verify email address

### Image Routes (/image)
- POST `/image/{patient_id}` - Upload an image for a patient
- GET `/image/patient/{patient_id}` - Get all images for a patient
- GET `/image/{image_id}` - Get specific image
- DELETE `/image/{image_id}` - Delete an image
- PATCH `/image/{image_id}` - Update image details

### ML Models Routes (/ml_models)
- POST `/ml_models/` - Retrieve ML model predictions

### Note Routes (/note)
- POST `/note/{patient_id}` - Create a note for a patient
- GET `/note/{note_id}` - Get specific note
- GET `/note/patient/{patient_id}` - Get all notes for a patient
- PATCH `/note/{note_id}` - Update a note
- DELETE `/note/{note_id}` - Delete a note

### Patient Routes (/patient)
- POST `/patient/` - Create a new patient
- GET `/patient/{patient_id}` - Get specific patient
- GET `/patient/` - Get all patients
- PATCH `/patient/{patient_id}` - Update patient information
- DELETE `/patient/{patient_id}` - Delete a patient

### Report Routes (/report)
- POST `/report/` - Create a new report
- GET `/report/{report_id}` - Get specific report
- PATCH `/report/{report_id}` - Update a report
- GET `/report/patient/{patient_id}` - Get all reports for a patient
- DELETE `/report/{report_id}` - Delete a report

### Statement Routes (/statement)
- POST `/statement/` - Create a new statement
- POST `/statement/initialize` - Initialize default statements
- GET `/statement/search` - Search statements by category
- GET `/statement/{statement_id}` - Get specific statement
- GET `/statement/` - Get all user statements
- PATCH `/statement/{statement_id}` - Update a statement
- DELETE `/statement/{statement_id}` - Delete/reset a statement

### User Routes (/user)
- GET `/user/` - Get current user profile
- PATCH `/user/` - Update user profile
- DELETE `/user/` - Delete user account

## Testing

1. Start docker

     ```
     docker compose build && docker compose up
     
     ```
2. Run the tests
   Either via the left panel and then "Testing" and "Run tests" on the left top or simply
   
     ```
     pytest -s
     
     ```
   (to also see the print statements)



