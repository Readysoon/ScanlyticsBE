from fastapi import HTTPException, status
from fastapi import Path
from typing import Annotated

from datetime import datetime
import logging
from pathlib import Path as PathLib



# Error Logging by Claude Sonnet:

# Create logs directory if it doesn't exist
LOGS_DIR = PathLib("logs")
LOGS_DIR.mkdir(exist_ok=True)

def get_logger():
    """Configure and return a logger instance for the current day"""
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"error_log_{today}.log"
    
    # Create a new logger
    logger = logging.getLogger(f'app_logger_{today}')
    
    # Only add handler if logger doesn't already have handlers
    if not logger.handlers:
        logger.setLevel(logging.ERROR)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
    
    return logger


# TEMPLATE
# raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"'error_stack'/'already contains' error.", e, UserSignupService)

class ErrorStack:
    def __init__(self):
        self.errors = []
        # Initialize logger in constructor
        self.logger = get_logger()

    def add_error(self, code, detail, e, function_name=None):
        if callable(function_name):
            function_name = function_name.__name__  
        else:
            function_name = str(function_name)

        # If the exception is an HTTPException, extract its detail
        if isinstance(e, HTTPException):
            exception_detail = e.detail
        else:
            exception_detail = str(e)

        error = {
            "code": code,
            "description": detail,
            "exception": exception_detail,  # Store the string representation
            "function": function_name
        }
        self.errors.append(error)

        # Log the error with structured information
        self.logger.error(
            f"Error in {function_name} - Code: {code} - Description: {detail} - Exception: {exception_detail}"
        )

        # Raise a new HTTPException with the original error detail
        raise HTTPException(
            status_code=code,
            detail=exception_detail
        )

    def get_last_error(self):
        if self.errors:
            last_error = self.errors[-1]
            return {
                "code": last_error['code'],
                "description": last_error['description'],
                "function": last_error.get('function', 'Unknown'),
                "exception": last_error.get('exception', 'Unknown error')
            }
        return None

    def __str__(self):
        error_str = ""
        for error in self.errors:
            error_str += (
                f"Code: {error['code']}, "
                f"Function: {error.get('function', 'Unknown')}, "
                f"Description: {error['description']}, "
                f"Exception: {error['exception']}\n"
            )
        return error_str.strip()


def ExceptionHelper(function_name, e, error_stack):

    # Get logger instance at function start
    logger = get_logger()

    if callable(function_name):
        function_name = function_name.__name__  
    else:
        function_name = str(function_name)

    # Log that ExceptionHelper was called
    logger.error(f"ExceptionHelper called for function: {function_name}")

    print("ExceptionHelper: ")
    # First check if error_stack exists
    if not error_stack:
        logger.error(error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stack is None: {str(e)}"
        )

    # Check for other errors
    last_error = error_stack.get_last_error()
    if last_error:
        print(f"{function_name}: Printed error stack: \n{error_stack}")
        if last_error['exception'] == "None":
            raise HTTPException(
            status_code=last_error["code"], 
            detail=f"{last_error['description']}"
            # above for production, below for development
            # detail=f"Function: {last_error.get('function', 'Unknown')}, Description: {last_error['description']}"
            )
        raise HTTPException(
            status_code=last_error["code"], 
            detail=f"{last_error['description']}"
            # above for production, below for development
            # detail=f"Function: {last_error.get('function', 'Unknown')}, Description: {last_error['description']}"
        )
    else:
        # If no error in stack but we have an exception
        error_msg = str(e) if e else "Unknown error occurred"
        print(f"No error in stack, using exception: {error_msg}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=error_msg
        )
    
def DatabaseErrorHelper(query_result, error_stack):
    try:
        if query_result is None:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    "Query result is None.", 
                    "None", 
                    DatabaseErrorHelper
                )
            
        elif 'status' not in query_result[0]:
            return query_result
        
        elif query_result[0]['status'] == 'ERR':
            if "already contains" in query_result[0]['result']:
                return query_result[0]['result']
            else: 
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "query_result[0]['status'] == 'ERR'",
                    "None",
                    DatabaseErrorHelper
                )
    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR, 
                f"Other error: {query_result}", 
                e, 
                DatabaseErrorHelper
            )
    
    
class IDValidator:
    min_length = 20
    max_length = 20
    pattern = r'^[a-zA-Z0-9]+$'
    description = "ID must be 20 characters long and contain only alphanumeric characters"
    
    ValidatedID = Annotated[str, Path(
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        description=description
    )]


class TokenValidator:
    min_length = 144
    max_length = 144
    pattern = r'^[a-zA-Z0-9._-]+$'
    description = f"Token must be 144 characters long"
    
    ValidatedToken = Annotated[str, Path(
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        description=description
    )]

        
