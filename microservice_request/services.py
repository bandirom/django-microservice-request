import logging
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from requests import Response as RequestResponse
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .decorators import request_shell
from .exceptions import MicroserviceException

logger = logging.getLogger(__name__)

JSONType = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]


class HostService:
    def __init__(self):
        self.session: Session = self.session_request()

    def session_request(self):
        session = Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session


class ConnectionService:
    lookup_prefix: str = ""
    service: str = None
    url: str = ""
    api_header: str = getattr(settings, "API_KEY_HEADER", "ACCESS-KEY")
    api_key: str = ""
    error_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    http_method_names: list = ("get", "post", "put", "patch", "delete")
    additional_methods: list = ["send_file"]
    custom_methods: list = []

    def __init__(self, url: str, **kwargs):
        self.special_headers: dict = kwargs.get("special_headers", {})
        self.host = HostService()
        self.set_url(str(url))

    @classmethod
    def microservice_response(cls, url: str, method: str, **kwargs):
        service = cls(url, **kwargs)
        return service.service_response(method=method, **kwargs)

    @property
    def get_method_names(self) -> list:
        return self.additional_methods + self.custom_methods

    @property
    def authorization_header(self) -> dict:
        return {"Authorization": f"{self.api_header} {self.api_key}"}

    def set_url(self, url: str) -> str:
        if url.startswith(self.lookup_prefix):
            url = url.replace(self.lookup_prefix, "", 1)
        self.url = urljoin(self.service or "", url)
        return self.url

    @staticmethod
    def reverse_url(url: str, kwargs: Optional[dict] = None) -> str:
        return reverse(url, kwargs=kwargs)

    @staticmethod
    def join_url(host: str, api: str) -> str:
        return urljoin(host, api)

    def custom_headers(self) -> dict:
        """Provide additional headers here"""
        return {}

    @property
    def headers(self) -> dict:
        headers: dict = self.authorization_header
        headers.update(self.special_headers if isinstance(self.special_headers, dict) else {})
        headers.update(self.custom_headers())
        return headers

    def http_method_not_allowed(self, method: str) -> None:
        logger.warning(
            f"Method Not Allowed: {method}. Add method to 'custom_methods' field",
            extra={"status_code": status.HTTP_405_METHOD_NOT_ALLOWED},
        )
        raise MethodNotAllowed(method)

    def _request_params(self) -> dict:
        return dict(url=self.url, headers=self.headers)

    @request_shell
    def _method(self, method: str, **kwargs) -> Optional[RequestResponse]:
        return self.host.session.request(method=method, **self._request_params(), **kwargs)

    @request_shell
    def send_file(self, files: dict, data: dict = None, **kwargs):
        request_data = self._request_params()
        request_data.update(data=data, files=files)
        return self.host.session.post(**request_data)

    def service_response(self, method: str, **kwargs) -> Response:
        response = self.request_to_service(method=method, **kwargs)
        if not getattr(response, "status_code", None):
            logger.error(f"Connection error in  {self.__str__()}, {method=}", extra=kwargs)
            return Response({"detail": "connection refused"}, status=self.error_status_code)
        return Response(
            data=self._response(response),
            status=response.status_code,
            headers=response.headers,
            content_type=response.headers.get("Content-Type"),
        )

    def request_to_service(self, method: str, **kwargs) -> RequestResponse:
        method: str = method.lower()
        if method in self.http_method_names:
            return self._method(method, **kwargs)
        elif method in self.get_method_names and (handler := getattr(self, method, None)):
            return handler(**kwargs)
        self.http_method_not_allowed(method)

    def _response(self, response: RequestResponse) -> JSONType:
        try:
            return response.json()
        except JSONDecodeError:
            return self.error_process()

    def error_process(self) -> None:
        raise MicroserviceException("Decode error")


class MicroServiceConnect(ConnectionService):
    SEND_COOKIES: bool = getattr(settings, "REQUEST_SEND_COOKIES", False)
    PROXY_REMOTE_USER: bool = False

    url_pagination_before = ""
    url_pagination_after = ""

    def __init__(self, request, url, **kwargs):
        super().__init__(url, **kwargs)
        self.request = request

    @property
    def headers(self) -> dict:
        headers: dict = {
            "Accept-Language": self.request.headers.get("Accept-Language"),
        }
        if self.PROXY_REMOTE_USER and not isinstance(self.request.user, AnonymousUser):
            headers.update({"Remote-User": str(self.request.user.id)})
        headers.update(super().headers)
        return headers

    @property
    def cookies(self) -> dict:
        return self.request.COOKIES

    def _request_params(self) -> dict:
        data: dict = super()._request_params()
        if self.SEND_COOKIES:
            data["cookies"] = self.cookies
        return data

    @request_shell
    def send_file(self, files: dict, data: dict = None, **kwargs):
        request_data: dict = self._request_params()
        request_data.update(data=data or self.request.data, files=files)
        return self.host.session.post(**request_data)

    def convert_service_url(self, url: str) -> str:
        """For pagination response"""
        url: str = url.replace(self.service, getattr(settings, "GATEWAY_HOST", self.request.get_host()))
        url: str = url.replace(self.url_pagination_before, self.url_pagination_after)
        return url

    def service_response(self, method: str = None, **kwargs) -> Response:
        method: str = method or self.request.method
        return super().service_response(method, **kwargs)
