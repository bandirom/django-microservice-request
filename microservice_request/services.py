import logging

from django.conf import settings
from requests import Session, Response as RequestResponse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR

from .decorators import request_shell

logger = logging.getLogger(__name__)


class HostService:
    def __init__(self):
        self.session = self.session_request()

    def session_request(self):
        session = Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session


class Service:
    lookup_prefix = ''
    service = None
    url = ''
    api_header = getattr(settings, 'API_KEY_HEADER', 'X-ACCESS-KEY')
    api_key = ''
    http_method_names = ['get', 'post', 'put', 'delete']

    def __init__(self):
        self.host = HostService()

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    @property
    def allowed_methods(self):
        return self._allowed_methods()

    @property
    def authorization_header(self) -> dict:
        return {"Authorization": f"{self.api_header} {self.api_key}"}

    def set_url(self, url) -> str:
        if url.startswith(self.lookup_prefix):
            url = url.replace(self.lookup_prefix, '', 1)
        self.url = f"{self.service}{url}"
        return self.url

    @staticmethod
    def reverse_url(url: str, kwargs=None):
        return reverse_lazy(url, kwargs=kwargs)


class MicroServiceConnect(Service):
    SEND_COOKIES = getattr(settings, 'REQUEST_SEND_COOKIES', False)
    url_pagination_before = ''
    url_pagination_after = ''
    additional_method_names = ['send_file']

    def __init__(self, request, url, **kwargs):
        super().__init__()
        self.set_url(str(url))
        self.request = request

    def http_method_not_allowed(self, **kwargs):
        method = kwargs.get('method', self.request.method)
        logger.warning(
            "Method Not Allowed (%s): %s. Add the name to 'additional_method_names'", method, self.request.path,
            extra={'status_code': 405, 'request': self.request}
        )
        raise MethodNotAllowed(method)

    def get_additional_method_names(self):
        return self.additional_method_names

    def custom_headers(self) -> dict:
        """Provide additional headers here"""
        return {}

    def connection_refused_error(self) -> str:
        """Logger error if connection refused"""
        return f"Connection error in  {self.__str__()}"

    @property
    def headers(self) -> dict:
        headers = super().authorization_header
        headers['Accept-Language'] = self.request.headers.get('Accept-Language')
        headers['Remote-User'] = str(self.request.user.id)
        headers.update(self.custom_headers())
        return headers

    def get_cookies(self) -> dict:
        return self.request.COOKIES

    def _requested_data(self) -> dict:
        data = dict(
            url=self.url,
            headers=self.headers,
            cookies=self.get_cookies() if self.SEND_COOKIES else None
        )
        return data

    @request_shell
    def get(self, params: dict = None, **kwargs):
        request_data = self._requested_data()
        request_data.update(params=params or self.request.GET)
        return self.host.session.get(**request_data)

    @request_shell
    def post(self, data: dict = None, **kwargs):
        request_data = self._requested_data()
        request_data.update(json=data or self.request.data)
        return self.host.session.post(**request_data)

    @request_shell
    def put(self, data: dict = None, **kwargs):
        request_data = self._requested_data()
        request_data.update(data=data or self.request.data)
        return self.host.session.put(**request_data)

    @request_shell
    def delete(self, **kwargs):
        request_data = self._requested_data()
        request_data.update(data=self.request.data)
        return self.host.session.delete(**request_data)

    @request_shell
    def send_file(self, files: dict, data: dict = None, **kwargs):
        request_data = self._requested_data()
        request_data.update(data=data or self.request.data, files=files)
        return self.host.session.post(**request_data)

    def convert_service_url(self, url: str) -> str:
        """For pagination response"""
        url = url.replace(self.service, getattr(settings, 'GATEWAY_HOST', self.request.get_host()))
        url = url.replace(self.url_pagination_before, self.url_pagination_after)
        return url

    def service_response(self, method: str = None, **kwargs):
        response = self.request_to_service(method=method, **kwargs)
        if not getattr(response, 'status_code', None):
            logger.error(self.connection_refused_error())
            return Response({'detail': 'connection refused'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response.json(), status=response.status_code)

    def request_to_service(self, method: str = None, **kwargs) -> RequestResponse:
        if not method:
            method = self.request.method
        if method.lower() in self.http_method_names or self.get_additional_method_names():
            handler = getattr(self, method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        kwargs['method'] = method
        return handler(**kwargs)
