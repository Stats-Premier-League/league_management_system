# DJANGO ADMIN CONFIGURATION 
# Main Purpose: To register and customize the core league data models
# (League, Season, Team, Player) within the Django Administration site.
# This makes it easy for administrators to view, search, filter, and manage the
# underlying data structure of the league management system.

from django.contrib import admin
from .models import League, Season, Team, Player

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'points_per_win', 'points_per_draw', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'country')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
     list_display = (
        'name', 'league', 'start_date', 'end_date', 
        'status', 'is_current', 'is_active'
    )
     list_filter = ('league', 'is_current', 'is_archived', 'is_active', 'competition_format')
     search_fields = ('name', 'league__name')
     date_hierarchy = 'start_date'
     readonly_fields = ('status', 'duration_days', 'days_remaining', 'match_completion_rate')
     fieldsets = (
        ('Basic Information', {
            'fields': ('league', 'name', 'slug', 'description', 'logo')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'registration_deadline')
        }),
        ('Status', {
            'fields': ('is_current', 'is_archived', 'status')
        }),
        ('Competition Rules', {
            'fields': (
                'competition_format',
                'points_per_win', 'points_per_draw', 'points_per_loss',
                'primary_tie_breaker', 'secondary_tie_breaker'
            )
        }),
        ('Financial', {
            'fields': ('registration_fee', 'prize_money'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('duration_days', 'days_remaining', 'match_completion_rate'),
            'classes': ('collapse',)
        })
    )
    
     def match_completion_rate(self, obj):
        return f"{obj.get_match_completion_rate()}%"
     match_completion_rate.short_description = 'Match Completion'
    
     def status(self, obj):
        return obj.status
     status.short_description = 'Status'
@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'code', 'primary_color', 'is_active')
    list_filter = ('league', 'is_active')
    search_fields = ('name', 'code', 'league__name')
    readonly_fields = ('primary_color_preview',)

    def primary_color_preview(self, obj):
        if obj.primary_color:
            return f'<div style="width: 50px; height: 20px; background-color: {obj.primary_color};"></div>'
        return '-'
        primary_color_preview.allow_tags = True
        primary_color_preview.shor_description = 'Color Preview'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'team', 'jersey_number', 'position', 'is_goalkeeper')
    list_filter = ('team_league', 'team', 'position', 'is_goalkeeper')
    search_fields = ('first_name', 'last_name', 'team_name')
    ordering = ('team', 'jersey_number')