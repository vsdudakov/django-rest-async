class RestException(Exception):
    pass


class RestValidateError(RestException):
    def __init__(self, errors_dict, status_code=400):
        self.errors_dict = errors_dict
        self.status_code = status_code


class RestForbiddenError(RestException):
    def __init__(self, error_str, status_code=403):
        self.errors_dict = {"meta": [error_str]}
        self.status_code = status_code


class RestNotFoundError(RestException):
    def __init__(self, error_str, status_code=404):
        self.errors_dict = {"meta": [error_str]}
        self.status_code = status_code
