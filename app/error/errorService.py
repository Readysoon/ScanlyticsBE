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
                "detail": last_error['detail'],
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
