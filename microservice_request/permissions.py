from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework.permissions import IsAuthenticated

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class HasApiKeyOrIsAuthenticated(IsAuthenticated):
    def has_permission(self, request: "Request", view: "APIView") -> bool:
        if key := request.headers.get("Authorization"):
            token: list = key.split(" ")
            if token[0] == settings.API_KEY_HEADER and token[1] == settings.API_KEY:
                return True
        return super().has_permission(request, view)
