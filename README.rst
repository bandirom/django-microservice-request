Microservice-Request
====================

Application for make sync requests (REST API) between microservices .

For testing you should have access to 2 or more projects (at least 1 project - should be Django Project)

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

3. In settings.py set the follow settings::

    # Custom api key header
    API_KEY_HEADER = os.environ.get('API_KEY_HEADER', 'X-Custom-Header')
    # Custom api key
    API_KEY = os.environ.get('API_KEY', 'api-secret-key')

    # Requested header will be:
    # Authorization: X-Custom-Header api-secret-key


For key generating recommend to use
https://florimondmanca.github.io/djangorestframework-api-key/



3. For example you have 2 deployed projects. First project will be ApiGateway and second will be ArticleBlog
    Create a new application for set separated route:


        docker-compose exec web python manage.py startapp router_article

    or

        python manage.py startapp router_article
