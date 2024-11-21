from functools import wraps
from traceback import format_exc

from django.conf import settings
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from utils.helper_functions import log_error


def api_safe_execution(function):
    @wraps(function)
    def _safe_execution(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            _, request = args
            request_path = request.path_info
            log_error(title=str(error), error=format_exc(), request=str(request.META))
            ## send email to develop
            #
            msg = EmailMessage(subject=str(error), body=format_exc(),
                               from_email=settings.EMAIL_HOST_USER, to=receiver)
            msg.content_subtype = "html"
            msg.send()
            if '/api/' in request_path:
                return Response(data="An error occurred, our engineers are on top of the situation, and it will be "
                                     "rectified in a bit", status=HTTP_400_BAD_REQUEST)

    return _safe_execution