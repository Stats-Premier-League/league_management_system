# DJANGO CUSTOM USER MODEL DEFINITION 
# Main Purpose: To define the Custom User Model (User) for the Django project.
# It extends Django's built-in authentication system (AbstractUser) to add
# project-specific fields (like role, phone, and team) and methods (like
# is_league_admin). By inheriting from BaseModel, it also includes standard
# audit fields (created_at, updated_at, is_active).

from django.contrib.auth.models import AbstractUser
from django.db import models

from .base import BaseModel

class User(AbstractUser, BaseModel):
    """
    Custom user model for the league management system
    """
    ROLE_CHOICES = [
        ('admin', 'League Administrator'),
        ('referee', 'Referee'),
        ('manager', 'Team Manager'),
        ('player', 'Player'),
        ('viewer', 'Viewer'),
        # Add more here
     ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='viewer'
    )
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )

    # Additional fields for different roles
    team = models.ForeignKey(
        'league.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def is_league_admin(self):
        return self.role == 'admin'

    def is_reference(self):
        return self.role == 'referee'

    def is_team_manager(self):
        return self.role == 'manager'

    def is_player(self):
        return self.role == 'player' 