# DJANGO ADMINISTRATIVE UTILITY SCRIPT 
# Main Purpose: This file is the main command-line utility for a Django project.
# It provides a convenient way to run administrative tasks (like runserver,
# makemigrations, migrate, createsuperuser, test, etc.) without needing
# to set up environment variables manually. It is the primary interface for
# interacting with the Django project during development.

"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed "
            "and available on your PYTHONPATH environment variables? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()