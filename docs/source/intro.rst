


Django application for make sync requests (REST API) between microservices or external APIs.


If you don't have any microservices yet, you can try to use `Django template`_

.. _Django template: https://github.com/bandirom/django-template


##########
Quickstart
##########


************
Installation
************

1. Install the package

.. code-block:: console

    $ pip install django-microservice-request

2. Usage (Google Captcha example)

`settings.py`

.. code-block:: python

    GOOGLE_CAPTCHA_URL = "https://google.com/recaptcha/api/siteverify"
    GOOGLE_CAPTCHA_SECRET_KEY = os.environ.get("GOOGLE_CAPTCHA_SECRET_KEY")

`services.py`

.. code-block:: python

    from django.conf import settings
    from microservice_request.services import ConnectionService

    class GoogleCaptchaService(ConnectionService):
        service = settings.GOOGLE_CAPTCHA_URL
        secret_key = settings.GOOGLE_CAPTCHA_SECRET_KEY

        def validate_captcha(self, captcha: str) -> dict:
            params = {
                "secret": self.secret_key,
                "response": captcha,
            }
            response = self.service_response(method="get", params=params)
            return response.data


`serializers.py`

.. code-block:: python

    from .services import GoogleCaptchaService

    class CaptchaMixinSerializer(serializers.Serializer):
        captcha = serializers.CharField()

        def validate_captcha(self, captcha: str) -> str:
            service = GoogleCaptchaService()
            response_data = service.validate_captcha(captcha)
            if not response_data.get("success"):
                raise serializers.ValidationError("Captcha validation error")
            return captcha

    class LoginSerializer(CaptchaMixinSerializer):
        login = serializers.CharField()
        password = serializers.CharField()
