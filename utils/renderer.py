from traceback import format_exc

from rest_framework.renderers import JSONRenderer

from base.constants import RESPONSE_MESSAGE
from utils.encryption_utils import encrypt_response
from utils.helper_functions import log_error


class CustomRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context.get("response").status_code
        if str(status_code).startswith("2"):
            response = {
                "success": True,
                "status_code": status_code,
                "data": encrypt_response(data) if data else dict(),
                "message": RESPONSE_MESSAGE.SUCCESS
            }

        else:
            response = {"success": False, "status_code": status_code, "message": RESPONSE_MESSAGE.FAILED}
            try:
                response["data"] = data
            except Exception as e:
                log_error(title=str(e), error=format_exc())
                pass

        return super(CustomRenderer, self).render(response, accepted_media_type, renderer_context)