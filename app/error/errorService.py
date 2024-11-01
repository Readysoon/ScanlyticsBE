from fastapi import HTTPException, status

class ErrorStack:
    def __init__(self):
        self.errors = []

    def add_error(self, code, detail, e, function_name=None):
        error = {
            "code": code,
            "description": detail,
            "exception": e,
            "function": function_name
        }
        self.errors.append(error)

    def get_last_error(self):
        if self.errors:
            # Return only code, function, and detail for the last error
            last_error = self.errors[-1]
            return {
                "code": last_error['code'],
                "description": last_error['description'],
                "function": last_error.get('function', 'Unknown')
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
    

def ExceptionHelper(function_name, query_result, error_stack, e):
    
    
    # First check if error_stack exists
    if error_stack is None:
        print(f"{function_name.__name__}: Printed error stack: \n{error_stack}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error stack is None: {str(e)}"
        )

    # If query_result is None, first add the error to the stack
    if query_result is None:
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Query execution failed",
            e,
            function_name.__name__
        )
        print(f"{function_name.__name__}: Printed error stack: \n{error_stack}")
        # Then get the last error
        last_error = error_stack.get_last_error()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Description: {last_error['description']}"
        )
    
    # Check for other errors
    last_error = error_stack.get_last_error()
    if last_error:
        print(f"{function_name.__name__}: Printed error stack: \n{error_stack}")
        raise HTTPException(
            status_code=last_error["code"], 
            detail=f"Function: {last_error.get('function', 'Unknown')}, Description: {last_error['description']}"
        )
    else:
        print(f"{function_name.__name__}: Printed error stack: \n{error_stack}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )
        
