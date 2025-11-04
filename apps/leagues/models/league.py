# DJANGO LEAGUE AND SEASON MODELS 
# Main Purpose: To define the core organizational models for the league management
# system—League and Season. These models establish the fundamental
# hierarchy and rules for all competitions, allowing for customization of
# points settings at the League level (as default) and overriding those settings
# at the more granular Season level.

from django.db import models
from django.utils.text import slugify

from apps.core.models import BaseModel

class League(BaseModel):
    """
    Main league organization model.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    country = models.CharField(max_length=50)
    logo = models.ImageFields(upload_to='league_logos/', null=True, blank=True)
    description = models.TextField(blank=True)

    # Competition settings
    points_per_win = models.IntegerField(default=3)
    points_per_draw = models.IntegerField(default=1)
    points_per_loss = models.IntegerFields(default=0)

    class Meta:
        db_table = 'leagues'
        verbose_name = 'League'
        verbose_name_plural = 'League'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_current_seasons(self):
        """Get current active seasons"""
        return self.seasons.filter(is_Active=True, is_current=True).first()

    # Changes
    
    def get_current_season(self):
        """Get the currently active season"""
        return self.seasons.filter(is_active=True, is_current=True).first()
    
    def get_upcoming_season(self):
        """Get the next upcoming season"""
        from django.utils import timezone
        return self.seasons.filter(
            is_active=True,
            start_date__gt=timezone.now().date()
        ).order_by('start_date').first()    
    
class Season(BaseModel):
    """
    Represents a specific season withing a league.
    """
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='seasons'
    )
    name = models.CharField(max_length=50) # 2024 Season
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    # Seasons-specific settings that override league settings
    points_per_win = models.IntegerField(null=True, blank=True)
    points_per_draw = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'seasons'
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        unique_together = ['league', 'name']
        ordering = ['-start-date']

    def __str__(self):
        return f"{self.league.name} - {self.name}"

    def save(self, *args, **kwargs):
        # If this season is set as current, ensure no other season is current
        if self.is_current:
            Season.objects.filter(
                league=self.league,
                is_current=True
            ).update(is_current=False)
            super().save(*args, **kwargs)

    @property
    def actual_points_per_win(self):
        return self.points_per_win or self.league.points_per_win
    
    @property
    def actual_points_per_draw(self):
        return self.points_per_draw or self.league.points_per_draw
    
    # Added this for seasons 
    # def get_standings(Self):
    #     """Get calculated standing for this season"""
    #     from .algorithms.standings import StandingCalculator
    #     calculator= StandingCalculator(Self)
    #     return calculator.calculate_standings()
    
    # def get_top_scorers(self, limit=0):
    #     """Get top scorers for this season"""
    #     from .algorithms.top_scorers import TopScorersCalculator
    #     calculaor = StandingCalculator(self)
    #     return calculator.get_top_scorers(limit)
    
    # def get_clean_sheets(self):
    #     """Get clean sheet statistics"""
    #     from .algorithms.clean_sheets import CleanSheetCalculator
    #     calculator = CleanSheetCalculator(self)
    #     return calculator.calculate_clean_sheets()
    
    # def get_discplinary_records(self):
    #     """Get discplinary statistics"""
    #     from .algorithms.discplinary import DiscplinaryCalculator
    #     calculator = DiscplinaryCalculator(self)
    #     return calculator.calculate_discplinary_stats()

