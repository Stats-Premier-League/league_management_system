# DJANGO APPLICATION CONFIGURATION 
# Main Purpose: To define the configuration for the matches Django application.
# This file is used by Django to register the application, set default settings,
# and provide a human-readable name for the admin interface.

from django.apps import AppConfig

class MatchesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.matches'
    verbose_name = 'Matches'