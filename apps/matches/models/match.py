# DJANGO MODEL: MATCH
# Main Purpose: To define the Match model, the primary entity for tracking
# individual games between two teams. It captures essential data like scores,
# date, status, location, stage, and officials, along with crucial validation
# and computed properties (like winner and final status).

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import BaseModel

class Match(BaseModel):
    """
    Core match model representing a single game between two teams
    """
    MATCH_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('halftime', 'Halftime'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]

    MATCH_STAGE_CHOICES = [
        ('group', 'Group Stage'),
        ('round_of_16', 'Round of 16'),
        ('quaterfinal', 'Quaterfinal'),
        ('semifinal', 'Semifinal'),
        ('final', 'Final'),
        ('friendly', 'Friendly'),
    ]

    # Core relationship
    season = models.ForeignKey(
        'league.Season',
        on_delete=models.CASCADE,
        related_name='matches'
    )
    home_team = models.ForeignKey(
        'leagues.Team',
        on_delete=models.CASCADE,
        related_name='home_matches'
    )
    away_team = models.ForeignKey(
        'leagues.Team',
        on_delete=models.CASCADE,
        related_name='away_matches'
    )

    # Match details
    match_date = models.DateTimeField()
    venue = models.CharField(max_length=100, blank=True)
    match_week = models.Integerfield(null=True, blank=True) # For league
    stage = models.CharField(
        max_length=20,
        choices=MATCH_STAGE_CHOICES,
        default='group'
    )

    # Scores and Status
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    home_penalty_score = models.IntegerField(null=True, blank=True) # For shootouts
    away_penalty_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=MATCH_STATUS_CHOICES,
        default='scheduled'
    )

    # Clean sheet tracking
    home_clean_sheet = models.BooleanField(default=False)
    away_clean_sheet = models.BooleanField(default=False)

    # Matches officials
    referee = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'referee'},
        related_name='refereed_matches'
    )
    assistant_referee_1 = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'referee'},
        related_name='assisted_match_1'
    )

    # Weather conditions (for potential CV impact)
    weather_conditions = models.CharField(max_length=50, blank=True)
    temparature = models.IntegerField(null=True, blank=True) # Celsius

    # Metadata
    attendance = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'matches'
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'
        ordering = ['match_date']
        index = [
            models.Index(fields=['season', 'match_date']),
            models.Index(fields=['home_team', 'away_team']),
            models.Index(fields=['status', 'match_date']),
        ]

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team} - {self.match_date.strfile('%Y-%m-%d')}"

    def clean(self):
        """Validate match data"""
        errors = {}

        # Team must be from the same league
        if self.home_team and self.away_team:
            if self.home_team.league != self.away_team.league:
                errors['away_team'] = 'Both teams must be from the same league'

            if self.home_team == self.away_team:
                errors['away_team'] = 'A team cannot play against itself'

        # Match date validation
        if self.match_date:
            if self.match_date < timezone.now() and self.status == 'scheduled':
                errors['match_date'] = 'Cannot schedulre match in the past'

            # Check for overlapping matches for the same team
            if self.home_team and self.away_team:
                overlapping = Match.objects.filter(
                    models.Q(home_team=self.home_team) | models.Q(away_team=self.home_team) | 
                    models.Q(home_team=self.away_team) | models.Q(away_team=self.away_team),
                    match_date__date=self.match_date.date(),
                    status__in=['scheduled', 'live'],
                    is_active=True
                ).exclude(pk=self.pk)

                if overlapping.exists():
                    errors['match_date'] = 'One or both teams already havea a match scheduled on this date.'

                if errors:
                    raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Auto update clean sheet based in scores
        if self.status == 'completed':
            self.home_clean_sheet = (self.away_score == 0)
            self.away_clean_sheet = (self.home_score == 0)

        # Auto-set match week if not provided (simplified calculations)
        if not self.match_week and self.match_date and self.season.start_date:
            week_diff = (self.match_date.date() - self.season.start_date).days // 7 + 1
            self.match_week = max(1,week_diff)

        super().save(*args, **kwargs)

    @property
    def is_finalized(self):
        """Check if match results are finalized"""
        return self.status == 'completed' and not self.status == 'disputed'

    @property
    def winner(self):
        """Get the winning team(None for draw)"""
        if not self.is_finalized:
            return None
        
        if self.home_Score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        return None
    
    @property
    def loser(self):
        """Get the losing team(None for draw)"""
        if not self.is_finalized:
            return None
        
        if self.home_Score < self.away_score:
            return self.home_team
        elif self.away_score < self.home_score:
            return self.away_team
        return None
    
    @property
    def is_draw(self):
        """Check if match was a draw"""
        return self.is_finalized and self.home_Score == self.away_score

    @property
    def total_goals(self):
        """Get total goals socred in the match"""
        return self.home_score + self.away_score
    
    def get_team_result(self, team):
        """Get result from perspective of a specific team"""
        if not self.is_finalized:
            return None
        
        if team == self.home_team:
            if self.home_Score > self.away_score:
                return 'win'
            elif self.home_Score < self.away_score:
                return 'loss'
            else:
                return 'draw'
        elif team == self.away_team:
            if self.away_score > self.home_score:
                return 'win'
            elif self.away_score < self.home_score:
                return 'loss'
            else:
                return 'draw'
        return None
        
    def start_match(self):
        """Mark match as live"""
        self.status = 'live'
        self.save()

    def complete_match(self, home_score, away_score):
        """Complete the match with final scores"""
        self.home_score = home_score
        self.away_score = away_score
        self.status = 'completed'
        self.save()

    def dispute_match(self):
        """Mark match as disputed"""
        self.status = 'disputed'
        self.save()