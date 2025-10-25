# DJANGO TEAM MODEL DEFINITION 
# Main Purpose: To define the Team database model, which stores all
# identifying information, metadata, and crucially, visual identification data
# (jersey colors and logos) necessary for the computer vision system to automatically
# track and differentiate teams during automated game analysis.

from django.db import models
from colorfield.fields import ColorField # install: pip install django-colorfield

from apps.core.models import BaseModel

class Team(BaseModel):
    """
    Team model with visual identification for computer visoin
    """
    league = models.ForeignKey(
        'leagues.League',
        on_delete=models.CASCADE,
        related_name='teams'
    )
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=50)
    code = models.CharField(max_length=5, unique=True) # "MUN", "ARS"

    # Visual identification for computer vision
    primary_color = ColorField(default='#FF0000') # Main jersey color
    secondary_color = ColorField(default='#FFFFFF') # Secondary color
    logo = models.ImageField(upload_to=100, blank=True)

    # Contact and metadata
    founded = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=100, blank=True)

    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        unique_together = ['league', 'name']

    def __str__(self):
        return f"{self.name} ({self.league.name})"

    def get_color_profiles(self):
        """
        Return a color information for computer vision tracking
        """
        return {
            'primary': self.primary_color,
            'secondary': self.secondary_color,
            'team_id': self.id,
            'code': self.code
        }