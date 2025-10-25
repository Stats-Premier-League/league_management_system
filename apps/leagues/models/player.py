# DJANGO PLAYER MODEL DEFINITION 
# Main Purpose: To define the Player database model, which stores all
# personal, physical, and team-related data for individual athletes in the league.
# It includes validation for the jersey number, enforces that a player's number
# is unique within their team, and contains fields specifically useful for future
# computer vision (CV) tracking (like height and weight).

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import BaseModel

class Player(BaseModel):
    """
    Player model with position and tracking information.
    """
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('CB', 'Center Back'),
        ('LB', 'Left Back'),
        ('RB', 'Right Back'),
        ('CDM', 'Defensive Midfilder'),
        ('CM', 'Center Midfielder'),
        ('CAM', 'Attacking Midfielder'),
        ('RW', 'Right Winger'),
        ('ST', 'Striker'),
        # add more
    ]

    team = models.ForegnKey(
        'league.Team',
        on_delete=models.CASCADE,
        related_name='players'
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    jersy_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)]
    )
    position =models.CharField(max_length=3, choice=POSITION_CHOICES)
    is_goalkeeper = models.BooleanField(default=False)

    # Physical attribute for potential CV tracking
    height_cm = models.IntegerField(null=True, blank=True) # Height in CM
    wight_kg = models.IntegerField(null=True, blank=True) # weight in KGS

    # Player metadata
    date_of_birth = models.DateField(null=True, blank=True)
    nationality =models.CharField(max_length=50, blank=True)
    profile_picture = models.ImageField(
        upload_to='player_profiles/',
        null=True,
        blank=True
    )

class Meta:
    db_table = 'players'
    verbose_name = 'Player'
    verbose_name_plural = 'Players'
    unique_together = ['team', 'jersey_number']
    ordering = ['team', 'jersey_number']

def __str__(self):
    return f"{self.first_name} {self.last_name} (#{self.jersey_number})"

@property
def full_name(self):
    return f"{self.first_name} {self.last_name}"

def save(self, *args, **kwargs):
    # Automatically set is_goalkeeper based on position
    self.is_goalkeeper = self.position == 'GK'
    super().save(*args, **kwargs)