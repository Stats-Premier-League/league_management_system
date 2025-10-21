# DJANGO DEVELOPMENT SETTINGS (Often settings/development.py)
#
# Main Purpose: This file OVERRIDES or ADDS to the base Django settings for
# use in a local development environment. Its goal is to maximize ease of
# debugging, visibility, and testing, while generally ignoring performance
# and production-level security concerns.

from .base import *

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

INTERNAL_IPS = ['127.0.0.1']

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}