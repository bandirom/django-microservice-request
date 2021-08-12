.. image:: https://img.shields.io/github/license/bandirom/django-microservice-request   :alt: GitHub


Microservice-Request
====================

Application for make sync requests (REST API) between microservices or external APIs.


If you don't have any microservice yet, please follow the link
https://github.com/bandirom/DjangoTemplateWithDocker

And deploy the project use the instruction in a link above



Quick start
-----------
1. Install the package
    pip install django-microservice-request

2. Add "microservice_request" to your INSTALLED_APPS::

    INSTALLED_APPS = [
        ...
        'microservice_request',
    ]

3. In settings.py set the follow settings. This settings needed for set access to your project like external service::

    # Custom api key header
    API_KEY_HEADER = os.environ.get('API_KEY_HEADER', 'X-Custom-Header')
    # Custom api key
    API_KEY = os.environ.get('API_KEY', 'your-api-secret-key')

    # Requested header will be:
    # Authorization: X-Custom-Header your-api-secret-key

    # Add permission to restframework block

    REST_FRAMEWORK = {
        'DEFAULT_PERMISSION_CLASSES': (
            'microservice_request.permissions.HasApiKeyOrIsAuthenticated',
        ),
    }


 Now You can handle all requests from external services which have header:
    `Authorization: X-Custom-Header your-api-secret-key`


    For key generating recommend to use
    https://florimondmanca.github.io/djangorestframework-api-key/


4. Sending requests to an external services:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


For example you need to send request to the Payment service with some specific headers


4.1 In settings.py::

    PAYMENT_API_URL = "http://host.com:8080"
    PAYMENT_API_KEY = "payment secret api key"

4.2 create a file services.py::


    from django.conf import settings
    from microservice_request.services import MicroServiceConnect

    class PaymentService(MicroServiceConnect):
        service = settings.PAYMENT_API_URL
        api_key = settings.PAYMENT_API_KEY


4.3 in your code (for example in views.py)::

    from .services import PaymentService

    def post(self, request, *args, **kwargs):
        """Ths method will work as proxy"""
        request_method = 'post'
        url = '/some/api/path/'
        data = {
            'key': 'value',
        }
        return PaymentService.microservice_response(
            request,
            reverse_url=url,
            method=request_method,
            data=data,
            special_headers={'IfNeed': 'SomeAdditionalHeader'}
        )
