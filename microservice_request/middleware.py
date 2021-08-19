from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject


class RemoteUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.remote_user = None
        if user_id := request.headers.get('Remote-User'):
            request.remote_user = int(user_id) if user_id.isdigit() else None
        elif request.user.is_authenticated:
            request.remote_user = SimpleLazyObject(lambda: request.user.id)
