from hashlib import sha256

from decouple import config
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

from .api_exceptions import (LoginRequiredException, EmailUnverifiedException)


class RequestAuthentication(BasePermission):

    def has_permission(self, request, view):

        try:
            request.META["HTTP_API_KEY"]
        except:
            raise PermissionDenied("Missing API Key !")
        try:
            HASH_KEY = request.META["HTTP_HASH_KEY"]
        except:
            raise PermissionDenied("Missing Hash key")

        try:
            id_key = request.META["HTTP_IDEMPOTENCY_KEY"]
        except:
            raise PermissionDenied("Missing Idempotency key")

        app_api_key = config("API_KEY", cast=str)
        app_secret_key = config("SECRET_KEY", cast=str)

        try:
            to_hash = app_api_key + app_secret_key + id_key
        except Exception as e:
            return False

        the_hash = sha256(to_hash.encode("utf8")).hexdigest()
        return the_hash == HASH_KEY


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return True
        raise LoginRequiredException


class ActiveUserPermission(BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            if request.user.is_account_verified:
                return True
            raise EmailUnverifiedException
        raise LoginRequiredException


