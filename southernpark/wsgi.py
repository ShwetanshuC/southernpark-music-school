import os
import traceback
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "southernpark.settings")

try:
    application = get_wsgi_application()
except Exception:
    _error = traceback.format_exc().encode()
    def application(environ, start_response):
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [_error]
