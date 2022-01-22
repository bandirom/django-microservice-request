from unittest import mock

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import path
from django.views.generic import TemplateView
from requests import Response
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response as DRFResponse
from rest_framework.reverse import reverse, reverse_lazy
from rest_framework.test import APITestCase

from microservice_request.decorators import request_shell
from microservice_request.exceptions import MicroserviceException
from microservice_request.services import ConnectionService
from microservice_request.test import RequestTestCaseMixin

User = get_user_model()

urlpatterns = [
    path("api/v1/test/", TemplateView.as_view(), name="test_external_url"),
]


class ConnectionServiceTestCase(RequestTestCaseMixin, APITestCase):
    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_simple_request(self, mocked_request):
        json_data = {"userId": 1, "id": 1, "title": "delectus aut autem", "completed": False}
        mock_resp = self._mock_response(json=json_data, status_code=status.HTTP_200_OK)
        mocked_request.return_value = mock_resp
        url = "https://jsonplaceholder.typicode.com/todos/1"
        service = ConnectionService(url)
        response = service.service_response("get")
        self.assertEqual(url, service.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, json_data)

    def test_http_method_names(self):
        api_methods = ("get", "post", "put", "patch", "delete")
        service = ConnectionService(url="")
        self.assertIsInstance(service.http_method_names, tuple)
        self.assertEqual(api_methods, service.http_method_names)

    def test_custom_method_names(self):
        service = ConnectionService(url="")
        self.assertIsInstance(service.get_method_names, list)
        self.assertEqual(service.get_method_names, ["send_file"])

    def test_authorization_header(self):
        service = ConnectionService(url="")
        self.assertEqual(service.authorization_header, {"Authorization": "ACCESS-KEY "})

    def test_headers(self):
        service = ConnectionService(url="")
        self.assertEqual(service.headers, {"Authorization": "ACCESS-KEY "})
        service = ConnectionService(url="", special_headers={"X-NEXT": "/login"})
        self.assertEqual(service.headers, {"Authorization": "ACCESS-KEY ", "X-NEXT": "/login"})

    def test_request_params(self):
        service = ConnectionService(url="http://web:8000")
        expected_params = {"url": "http://web:8000", "headers": {"Authorization": "ACCESS-KEY "}}
        self.assertEqual(service._request_params(), expected_params)

    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_json_exception(self, mocked_request):
        data = "<html><head><title>502 Bad Gateway</title></head></html>"
        mock_resp = Response()
        mock_resp.status_code = status.HTTP_502_BAD_GATEWAY
        mock_resp.data = data
        mocked_request.return_value = mock_resp
        service = ConnectionService(url="http://localhost:9000")

        with self.assertRaises(MicroserviceException):
            service.service_response("post", data={"key": "value"})

    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_wrong_request(self, mocked_request):
        mocked_request.return_value = None
        service = ConnectionService(url="http://localhost:9000")
        response = service.service_response("post", data={"key": "value"})
        self.assertIsInstance(response, DRFResponse)
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data, {"detail": "connection refused"})

    def test_method_not_allowed(self):
        service = ConnectionService(url="http://localhost:9000")
        with self.assertRaises(MethodNotAllowed):
            service.service_response("option", data={"key": "value"})

    def test_url_join(self):
        url = ConnectionService.join_url(host="http://localhost:9000", api="api/v1/test/")
        self.assertEqual(url, "http://localhost:9000/api/v1/test/")


@override_settings(ROOT_URLCONF="tests.test_services")
class ChildServiceTestCase(RequestTestCaseMixin, APITestCase):
    class TestConnectionService(ConnectionService):
        api_key = "12345-qwerty-98765"
        service = "https://api.external-service.com"
        custom_methods = ["send_cbor_encoded_data"]

        def custom_headers(self) -> dict:
            return {
                "X-Custom-Field": "ABC",
            }

        @request_shell
        def send_cbor_encoded_data(self, **kwargs):
            return self._method("post", data=kwargs.get("data"))

    def setUp(self):
        self.service = self.TestConnectionService(url="/api/v1/connect")

    def test_auth_api_keys(self):
        self.assertEqual(
            self.service.authorization_header, {"Authorization": "ACCESS-KEY 12345-qwerty-98765"}
        )

    def test_request_url(self):
        self.assertEqual(self.service.url, "https://api.external-service.com/api/v1/connect")
        self.service.set_url("without/prefix/slash/")
        self.assertEqual(self.service.url, "https://api.external-service.com/without/prefix/slash/")
        self.service.set_url(reverse("test_external_url"))
        self.assertEqual(self.service.url, "https://api.external-service.com/api/v1/test/")
        self.service.set_url(reverse_lazy("test_external_url"))
        self.assertEqual(self.service.url, "https://api.external-service.com/api/v1/test/")
        service = self.TestConnectionService(reverse("test_external_url"))
        self.assertEqual(service.url, "https://api.external-service.com/api/v1/test/")
        url = self.TestConnectionService.reverse_url("test_external_url")
        service = self.TestConnectionService(url)
        self.assertEqual(service.url, "https://api.external-service.com/api/v1/test/")

    def test_custom_methods(self):
        self.assertEqual(self.service.get_method_names, ["send_file", "send_cbor_encoded_data"])

    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_request_through_custom_method(self, mocked_request):
        json_data = {"detail": True}
        mock_resp = self._mock_response(json=json_data, status_code=status.HTTP_200_OK)
        mocked_request.return_value = mock_resp
        response = self.service.service_response("send_cbor_encoded_data", data="asdk4lj2asdlhy1231")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, json_data)

    @mock.patch("microservice_request.services.ConnectionService._method")
    def test_microservice_request_class_method(self, mocked_request):
        json_data = {"detail": True}
        mock_resp = self._mock_response(json=json_data, status_code=status.HTTP_200_OK)
        mocked_request.return_value = mock_resp
        url = "/oauth/init/"
        response = self.TestConnectionService.microservice_response(url, "post", data={"status": True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, json_data)
