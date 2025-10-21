# DJANGO ABSTRACT BASE MODEL DEFINITION 
# Main Purpose: To define an Abstract Base Model (BaseModel) that provides
# a standardized set of common, essential fields and methods to be inherited
# by all other models (e.g., Team, Player, Match) in the application. This enforces
# consistency (DRY - Don't Repeat Yourself) across the entire database schema.

from django.db import models

class BaseModel(models.Model):
    """
    Abstract base model witth common field for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the instance"""
        self.is_active = False
        self.save()    