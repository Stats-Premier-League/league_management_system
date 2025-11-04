# DJANGO MODEL MODULE EXPORT
# Main Purpose: To aggregate and export the core Django models from the
# apps.matches application's model directory. This allows other parts of the
# Django project (like admin.py, views.py, or other applications) to import
# all relevant match-related models using a single, clean import statement

from .match import Match
from .event import MatchEvent
from .lineup import Lineup, Substitution
from .submission import MatchSubmission

__all__ = ['Match', 'MatchEvent', 'Lineup', 'Substitution', 'MatchSubmission']