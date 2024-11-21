from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from utils.authorization_utils import RequestAuthentication


class AllowAnyMixin(APIView):
    Authentication_classes = []
    permission_classes = (RequestAuthentication, AllowAny,)