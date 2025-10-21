# DJANGO APPLICATION CONFIGURATION 
# Main Purpose: This file provides metadata and configuration for a specific
# Django application, in this case, the 'core' application. It tells Django
# how to identify and manage the app when the project starts up.

from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.modles.BigAutoFields'
    name = 'apps.core'
    verbose_name = 'Core'