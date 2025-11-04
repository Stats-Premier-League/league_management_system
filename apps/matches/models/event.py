# DJANGO MODEL: MATCH EVENT
# Main Purpose: To define the MatchEvent model, which tracks every discrete
# action or occurrence within a match, providing detailed data for statistics
# calculation (goals, cards, substitutions, location data, etc.).

from django.db import models
from django.core.exceptions import ValidationError

from apps.core.models import BaseModel


class MatchEvent(BaseModel):
    """
    Individual events that occur during a match (goals, cards, substitutions, etc.)
    """
    EVENT_TYPE_CHOICES = [
        # Goals
        ('goal', 'Goal'),
        ('penalty_goal', 'Penalty Goal'),
        ('own_goal', 'Own Goal'),
        ('missed_penalty', 'Missed Penalty'),
        
        # Cards
        ('yellow_card', 'Yellow Card'),
        ('red_card', 'Red Card'),
        ('second_yellow', 'Second Yellow Card'),
        
        # Substitutions
        ('substitution_in', 'Substitution In'),
        ('substitution_out', 'Substitution Out'),
        
        # Other
        ('assist', 'Assist'),
        ('penalty_awarded', 'Penalty Awarded'),
        ('foul', 'Foul'),
        ('offside', 'Offside'),
        ('corner', 'Corner'),
        ('free_kick', 'Free Kick'),
        ('injury', 'Injury'),
        ('var_decision', 'VAR Decision'),
    ]
    
    # Core relationships
    match = models.ForeignKey(
        'matches.Match',
        on_delete=models.CASCADE,
        related_name='events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    
    # Primary player involved
    player = models.ForeignKey(
        'leagues.Player',
        on_delete=models.CASCADE,
        related_name='match_events'
    )
    
    # Secondary player (for assists, substitutions, etc.)
    related_player = models.ForeignKey(
        'leagues.Player',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='related_events'
    )
    
    # Event details
    minute = models.IntegerField()  # Match minute when event occurred
    extra_time = models.IntegerField(default=0)  # Injury time minute
    team = models.ForeignKey(
        'leagues.Team',
        on_delete=models.CASCADE,
        related_name='match_events'
    )
    
    # Event-specific flags
    is_penalty = models.BooleanField(default=False)
    is_own_goal = models.BooleanField(default=False)
    is_var_confirmed = models.BooleanField(default=False)
    
    # Location data (for potential CV integration)
    pitch_area_x = models.FloatField(null=True, blank=True)  # 0-100, left to right
    pitch_area_y = models.FloatField(null=True, blank=True)  # 0-100, goal to goal
    
    # Additional metadata
    description = models.TextField(blank=True)
    video_timestamp = models.CharField(max_length=20, blank=True)  # For video review

    class Meta:
        db_table = 'match_events'
        verbose_name = 'Match Event'
        verbose_name_plural = 'Match Events'
        ordering = ['match', 'minute', 'extra_time']
        indexes = [
            models.Index(fields=['match', 'event_type']),
            models.Index(fields=['player', 'event_type']),
            models.Index(fields=['team', 'event_type']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.player} ({self.minute}')"

    def clean(self):
        """Validate event data"""
        errors = {}
        
        # Player must be from the event team
        if self.player and self.team:
            if self.player.team != self.team:
                errors['player'] = 'Player must be from the event team.'
        
        # Related player validation
        if self.related_player and self.related_player.team != self.team:
            errors['related_player'] = 'Related player must be from the same team.'
        
        # Minute validation
        if self.minute < 0 or self.minute > 120:
            errors['minute'] = 'Minute must be between 0 and 120.'
        
        if self.extra_time < 0 or self.extra_time > 15:
            errors['extra_time'] = 'Extra time must be between 0 and 15.'
        
        # Event-specific validations
        if self.event_type == 'assist' and not self.related_player:
            errors['related_player'] = 'Assist events require a related player (goalscorer).'
        
        if self.event_type in ['substitution_in', 'substitution_out'] and not self.related_player:
            errors['related_player'] = 'Substitution events require a related player.'
        
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Auto-set flags based on event type
        if self.event_type == 'own_goal':
            self.is_own_goal = True
        
        if self.event_type == 'penalty_goal':
            self.is_penalty = True
        
        # Auto-set team based on player if not provided
        if not self.team and self.player:
            self.team = self.player.team
        
        super().save(*args, **kwargs)

    @property
    def is_goal_event(self):
        """Check if this event represents a goal"""
        return self.event_type in ['goal', 'penalty_goal', 'own_goal']

    @property
    def is_card_event(self):
        """Check if this event represents a card"""
        return self.event_type in ['yellow_card', 'red_card', 'second_yellow']

    @property
    def is_substitution_event(self):
        """Check if this event represents a substitution"""
        return self.event_type in ['substitution_in', 'substitution_out']

    @property
    def full_minute(self):
        """Get full minute including extra time"""
        if self.extra_time > 0:
            return f"{self.minute}+{self.extra_time}"
        return str(self.minute)

    def get_opposing_team(self):
        """Get the opposing team in the match"""
        if self.team == self.match.home_team:
            return self.match.away_team
        return self.match.home_team