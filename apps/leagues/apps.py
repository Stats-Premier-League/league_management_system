# DJANGO APPLICATION CONFIGURATION 
# Main Purpose: To define the metadata and configuration for the specific
# Django application responsible for managing all league-related data. This file
# registers the application with Django and provides a readable name for it,
# ensuring the framework knows how to identify and manage the 'leagues' module.

from django.apps import AppConfig

class LEaguesConfig(AppConfig):
    """
    Django application configuration for the leagues modules.
    """
    default_auto_field = 'sjango.db.models.BigAutoFields'
    name = 'apps.leagues'
    verbose_name = 'Leagues'