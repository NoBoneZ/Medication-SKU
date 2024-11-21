from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_401_UNAUTHORIZED


class EmailUnverifiedException(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = "The user email is not verified"


class LoginRequiredException(APIException):
    status_code = HTTP_401_UNAUTHORIZED
    default_detail = "Login is required to access this view"