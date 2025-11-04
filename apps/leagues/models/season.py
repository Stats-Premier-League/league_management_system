# DJANGO MODEL: SEASON eagues/models/season.py)
# Main Purpose: To define the Season model, which is the central entity for
# organizing a league's competitive cycle. It encapsulates all season-specific data,
# including dates, rules (points, tie-breakers), status, and convenient property
# and method shortcuts to access calculated statistics and metadata.

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import BaseModel


class Season(BaseModel):
    """
    Represents a specific season within a league with time-bound competition.
    """
    league = models.ForeignKey(
        'leagues.League',
        on_delete=models.CASCADE,
        related_name='seasons'
    )
    name = models.CharField(max_length=100)  # e.g., "2024 Premier League Season"
    slug = models.SlugField(max_length=110, blank=True)
    
    # Season duration
    start_date = models.DateField()
    end_date = models.DateField()
    registration_deadline = models.DateField(null=True, blank=True)
    
    # Season status
    is_current = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Season-specific rules that override league defaults
    points_per_win = models.IntegerField(null=True, blank=True)
    points_per_draw = models.IntegerField(null=True, blank=True)
    points_per_loss = models.IntegerField(null=True, blank=True)
    
    # Competition format
    COMPETITION_FORMAT_CHOICES = [
        ('league', 'Round Robin League'),
        ('knockout', 'Knockout Tournament'),
        ('group_knockout', 'Group Stage + Knockout'),
        ('double_elimination', 'Double Elimination'),
    ]
    competition_format = models.CharField(
        max_length=20,
        choices=COMPETITION_FORMAT_CHOICES,
        default='league'
    )
    
    # Tie-breaker rules
    TIE_BREAKER_1_CHOICES = [
        ('goal_difference', 'Goal Difference'),
        ('goals_for', 'Goals For'),
        ('head_to_head', 'Head-to-Head'),
        ('away_goals', 'Away Goals'),
    ]
    TIE_BREAKER_2_CHOICES = [
        ('goals_for', 'Goals For'),
        ('head_to_head', 'Head-to-Head'),
        ('away_goals', 'Away Goals'),
        ('goal_difference', 'Goal Difference'),
    ]
    
    primary_tie_breaker = models.CharField(
        max_length=20,
        choices=TIE_BREAKER_1_CHOICES,
        default='goal_difference'
    )
    secondary_tie_breaker = models.CharField(
        max_length=20,
        choices=TIE_BREAKER_2_CHOICES,
        default='goals_for'
    )
    
    # Financial settings
    registration_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    prize_money = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Metadata
    description = models.TextField(blank=True)
    logo = models.ImageField(
        upload_to='season_logos/',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'seasons'
        verbose_name = 'Season'
        verbose_name_plural = 'Seasons'
        unique_together = ['league', 'name']
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['league', 'start_date']),
            models.Index(fields=['is_current', 'is_active']),
        ]

    def __str__(self):
        return f"{self.league.name} - {self.name}"

    def clean(self):
        """Validate season data before saving"""
        errors = {}
        
        # Date validation
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                errors['end_date'] = 'End date must be after start date.'
            
            # Check for overlapping seasons in the same league
            overlapping_seasons = Season.objects.filter(
                league=self.league,
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
                is_active=True
            ).exclude(pk=self.pk)
            
            if overlapping_seasons.exists():
                errors['start_date'] = 'This season overlaps with an existing season.'
        
        # Points validation
        if self.points_per_win is not None and self.points_per_win < 0:
            errors['points_per_win'] = 'Points per win cannot be negative.'
        
        if self.points_per_draw is not None and self.points_per_draw < 0:
            errors['points_per_draw'] = 'Points per draw cannot be negative.'
        
        if self.points_per_loss is not None and self.points_per_loss < 0:
            errors['points_per_loss'] = 'Points per loss cannot be negative.'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(f"{self.league.name} {self.name}")
            self.slug = base_slug
            
            # Ensure uniqueness
            counter = 1
            while Season.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # If this season is set as current, ensure no other season is current
        if self.is_current and self.is_active:
            Season.objects.filter(
                league=self.league,
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        # Auto-set is_archived based on end date
        if self.end_date and self.end_date < timezone.now().date():
            self.is_archived = True
            self.is_current = False
        
        super().save(*args, **kwargs)

    @property
    def status(self):
        """Get human-readable status of the season"""
        today = timezone.now().date()
        
        if self.is_archived:
            return "archived"
        elif self.is_current:
            return "current"
        elif self.start_date > today:
            return "upcoming"
        elif self.start_date <= today <= self.end_date:
            return "active"
        else:
            return "completed"

    @property
    def actual_points_per_win(self):
        """Get effective points per win (season override or league default)"""
        return self.points_per_win if self.points_per_win is not None else self.league.points_per_win

    @property
    def actual_points_per_draw(self):
        """Get effective points per draw (season override or league default)"""
        return self.points_per_draw if self.points_per_draw is not None else self.league.points_per_draw

    @property
    def actual_points_per_loss(self):
        """Get effective points per loss (season override or league default)"""
        return self.points_per_loss if self.points_per_loss is not None else self.league.points_per_loss

    @property
    def duration_days(self):
        """Get the duration of the season in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0

    @property
    def days_remaining(self):
        """Get days remaining in the season (negative if completed)"""
        if not self.end_date:
            return None
        
        today = timezone.now().date()
        return (self.end_date - today).days

    def get_participating_teams(self):
        """Get all teams participating in this season"""
        from .team import Team
        return Team.objects.filter(league=self.league, is_active=True)

    def get_total_matches(self):
        """Get total number of matches in this season"""
        try:
            from apps.matches.models import Match
            return Match.objects.filter(season=self).count()
        except ImportError:
            return 0

    def get_completed_matches(self):
        """Get number of completed matches"""
        try:
            from apps.matches.models import Match
            return Match.objects.filter(season=self, status='completed').count()
        except ImportError:
            return 0

    def get_match_completion_rate(self):
        """Get percentage of matches completed"""
        total = self.get_total_matches()
        if total == 0:
            return 0
        completed = self.get_completed_matches()
        return round((completed / total) * 100, 1)

    def activate(self):
        """Mark this season as current and active"""
        self.is_current = True
        self.is_archived = False
        self.save()

    def archive(self):
        """Archive this season"""
        self.is_current = False
        self.is_archived = True
        self.save()

    def get_standings(self):
        """Get calculated standings for this season"""
        from ..algorithms.standings import StandingsCalculator
        calculator = StandingsCalculator(self)
        return calculator.calculate_standings()

    def get_top_scorers(self, limit=10):
        """Get top scorers for this season"""
        from ..algorithms.top_scorers import TopScorersCalculator
        calculator = TopScorersCalculator(self)
        return calculator.get_top_scorers(limit)

    def get_clean_sheets(self):
        """Get clean sheet statistics"""
        from ..algorithms.clean_sheets import CleanSheetCalculator
        calculator = CleanSheetCalculator(self)
        return calculator.calculate_clean_sheets()

    def get_disciplinary_stats(self):
        """Get disciplinary statistics"""
        from ..algorithms.disciplinary import DisciplinaryCalculator
        calculator = DisciplinaryCalculator(self)
        return calculator.calculate_disciplinary_stats()

    def get_tie_breaker_rules(self):
        """Get the ordered list of tie-breaker rules"""
        rules = [self.primary_tie_breaker]
        if self.secondary_tie_breaker and self.secondary_tie_breaker != self.primary_tie_breaker:
            rules.append(self.secondary_tie_breaker)
        return rules

    def is_registration_open(self):
        """Check if registration is still open for this season"""
        if not self.registration_deadline:
            return self.status in ["upcoming", "active"]
        
        today = timezone.now().date()
        return today <= self.registration_deadline and self.status in ["upcoming", "active"]