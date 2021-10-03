from json import dumps
from hashlib import md5
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class HasApiKeyOrIsAuthenticated(IsAuthenticated):

    def has_permission(self, request, view):
        if key := request.headers.get('Authorization'):
            token = list(key.split(" "))
            if token[0] == settings.API_KEY_HEADER and token[1] == settings.API_KEY:
                return True
        return super().has_permission(request, view)


class HashInHeaderOrIsAdmin(IsAdminUser):
    methods = ['POST', 'PUT', 'PATCH']

    def has_permission(self, request, view):
        header_hash = request.headers.get(getattr(settings, 'HASH_HEADER', 'X-Hash'))
        data_hash: str = md5(dumps(request.data).encode('utf-8')).hexdigest()
        if request.method in self.methods:
            return header_hash == data_hash
        return True
