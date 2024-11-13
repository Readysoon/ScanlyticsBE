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

Architecture/Security:

https://miro.com/app/board/uXjVLYDG24o=/?share_link_id=101772163535

API End Point explanation:



