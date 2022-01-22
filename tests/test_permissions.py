from base64 import b64encode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import path
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework.views import APIView

from microservice_request.permissions import HasApiKeyOrIsAuthenticated

User = get_user_model()


class PermissionTestView(APIView):
    permission_classes = (HasApiKeyOrIsAuthenticated,)

    def post(self, request):
        return Response({"detail": "OK"}, status=status.HTTP_200_OK)


urlpatterns = [
    path("view/without-auth/", PermissionTestView.as_view(authentication_classes=()), name="api_permission"),
    path(
        "view/session/",
        PermissionTestView.as_view(authentication_classes=(SessionAuthentication,)),
        name="session_view_permission",
    ),
    path(
        "view/basic/",
        PermissionTestView.as_view(authentication_classes=(BasicAuthentication,)),
        name="basic_view_permission",
    ),
]


@override_settings(ROOT_URLCONF="tests.test_permissions")
class PermissionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test_admin",
            password="test_password",
        )
        cls.url_without_auth = reverse("api_permission")
        cls.url_session_auth = reverse("session_view_permission")
        cls.url_basic_auth = reverse("basic_view_permission")

    def test_forbidden_api_keys(self):
        data = {"key": "value"}
        response = self.client.post(self.url_without_auth, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_api_keys(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"{settings.API_KEY_HEADER} {settings.API_KEY}")
        data = {"key": "value"}
        response = self.client.post(self.url_without_auth, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "OK"})

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]
    )
    def test_auth_user_with_session_auth(self):
        self.client.login(username="test_admin", password="test_password")
        data = {"key": "value"}
        response = self.client.post(self.url_session_auth, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "OK"})

    def test_auth_user_with_basic_auth(self):
        data = {"key": "value"}
        headers = {
            "HTTP_AUTHORIZATION": "Basic {}".format(
                b64encode("test_admin:test_password".encode()).decode("ascii")
            )
        }
        response = self.client.post(self.url_basic_auth, data, **headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "OK"})
