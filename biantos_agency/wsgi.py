"""
WSGI config for biantos_agency project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

# import os
# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biantos_agency.settings')
# application = get_wsgi_application()


import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biantos_agency.settings')

_application = get_wsgi_application()

def application(environ, start_response):
    def clean_start_response(status, headers, exc_info=None):
        cleaned_headers = [(k, v.lstrip()) for k, v in headers]
        return start_response(status, cleaned_headers, exc_info)
    return _application(environ, clean_start_response)
