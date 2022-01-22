import logging
from functools import wraps

from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def except_shell(errors=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except errors as e:
                logging.error(e)
                return None

        return wrapper

    return decorator


request_shell = except_shell((RequestException,))
