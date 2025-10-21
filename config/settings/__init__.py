# DJANGO SETTINGS ENTRY POINT (Often settings/__init__.py)
#
# Main Purpose: To establish a single, unified configuration file that dynamically
# loads environment-specific settings (like development, staging, or production)
# on top of a common set of base settings. This creates a flexible and robust
# configuration system for different deployment stages.

from .base import *

# Import environment-specific settings
try:
    from .development import *
except ImportError:
    pass

try:
    from .production import *
except ImportError:
     pass    