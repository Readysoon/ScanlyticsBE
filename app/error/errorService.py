class ErrorStack:
    def __init__(self):
        self.errors = []

    def add_error(self, code, detail, function_name=None):
        error = {
            "code": code,
            "detail": detail,
            "function": function_name
        }
        self.errors.append(error)

    def get_last_error(self):
        if self.errors:
            return self.errors[-1]
        return None

    def __str__(self):
        error_str = ""
        for error in self.errors:
            error_str += f"Code: {error['code']}, Function: {error.get('function', 'Unknown')}, Detail: {error['detail']}\n"
        return error_str.strip()
