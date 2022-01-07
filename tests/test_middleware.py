from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils.functional import SimpleLazyObject
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory, APITestCase

from microservice_request.middleware import RemoteUserMiddleware

User = get_user_model()


@override_settings(
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "microservice_request.middleware.RemoteUserMiddleware",
    ],
)
class MiddlewareTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test_admin",
            password="test_password",
        )

    @staticmethod
    def dummy_get_response(request):
        return request

    def setUp(self, *args, **kwargs):
        self.factory = APIRequestFactory()
        self.wrapped_request = self.factory.get("/")
        self.request = Request(self.wrapped_request)
        self.middleware = RemoteUserMiddleware(get_response=self.dummy_get_response(self.request))

    def test_request_no_props(self):
        request = self.factory.get("/")
        self.middleware.process_request(request)
        self.assertIsNone(request.remote_user)

    def test_request_with_header(self):
        request = self.factory.get("/", **{"HTTP_REMOTE_USER": "1"})
        self.middleware.process_request(request)
        self.assertIsInstance(request.remote_user, int)
        self.assertEqual(request.remote_user, 1)

    def test_request_auth_user(self):
        request = self.factory.get("/")
        request.user = self.user
        self.middleware.process_request(request)
        self.assertIsInstance(request.remote_user, SimpleLazyObject)
        self.assertEqual(request.remote_user, 1)
