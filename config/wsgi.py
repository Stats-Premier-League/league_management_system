# DJANGO WSGI CONFIGURATION 
# Main Purpose: This file serves as the entry point for a production-level
# Python web server (like Gunicorn or uWSGI) to communicate with the Django
# application. WSGI (Web Server Gateway Interface) is the standard interface
# between Python web applications and web servers.

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()