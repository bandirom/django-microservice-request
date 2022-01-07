import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

API_KEY_HEADER = "ACCESS-KEY"
API_KEY = os.environ.get("API_KEY", "JD6BComQ.FgBgwk2xnwjPaBtJD3PLbGwlqg25AtHc")


DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

ROOT_URLCONF = "tests.urls"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

MIDDLEWARE = []

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (),
    "DEFAULT_PERMISSION_CLASSES": (),
}


SECRET_KEY = os.environ.get("SECRET_KEY", "38dh*skf8sjfhs287dh&^hd8&3hdg*j2&sd")

USE_TZ = True

TIME_ZONE = "UTC"
