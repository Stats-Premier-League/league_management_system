# LEAGUE TOP SCORERS CALCULATOR CLASS 
# Main Purpose: To define the TopScorersCalculator class, which is responsible
# for calculating and retrieving individual player statistical leaders for a
# given season. Specifically, it uses Django's ORM (Object-Relational Mapper)
# aggregation functions to efficiently query match event data and compile lists
# of the top goal scorers and top assist providers.

from django.db.models import Count, Q
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class PlayerStats:
    """
    Data structures for player statistics.
    """
    player_id: int
    player_name: str
    team_name: str
    goals: int = 0
    assists: int= 0
    matches_played: int = 0

class TopScorersCalculaor:
    """
    Calculate top scorers and assist leaders 
    """

    def __init__(self, season):
        self.season = season

    def get_top_scorers(self, limit: int = 10) -> List[PlayerStats]:
        """
        Get top goal scorers for the season
        """
        from apps.matches.models import MatchEvent
        from apps.leagues.models import Player

        # Get goal events for this season
        goal_events = MatchEvent.objects.filter(
            match__season=self.season,
            event_type__in=['goal', 'penalty_goal']
        ).exclude(is_own_goal=True) # Exclude own goals

        # Aggregate gaols by player
        goals_by_player = goal_events.values(
            'player_id',
            'player__first_name',
            'player__last_name',
            'player__team__name'
        ).annotate(
            total_goals=Count('id')
        ).order_by('-total_goals')[:limit]

        # Convert to playStats objects
        top_scorers = []
        for item in goals_by_player:
            stats = PlayerStats(
                player_id=item['player-id'],
                player_name=f"{item['player__first_name']} {item['player__last_name']}",
                team_name=item['player__team__name'],
                goals=item['total_goals']
            )
            top_scores.append(stats)

        return top_scorers

    def get_top_assists(self, limit: int = 10) -> List[PlayerStats]:
        """
        Get top assist providers for the season
        """
        from apps.matches.models import MatchEvent

        # Get assist events for this season
        assist_events = MatchEvent.objects.filter(
            match__season=self.season,
            event_type='assist'
        )

        # Aggregate assists by player
        assists_by_player = assist_events.values(
            'player_id',
            'player__first_name',
            'player__last_name',
            'player__team_name'
        ).annotate(
            total_assists=Count('id')
        ).order_by('-total_assists')[:limit]

        # Convert to PlayerStats objects
        top_assists = []
        for item in assists_by_player:
            stats = PlayerStats(
                player_id=item['player_id'],
                player_name=f"{item['player__first_name']} {item['player__last_name']}",
                team_name=item['player__team_name'],
                assists=item['total_assists']
            )
            top_assists.append(stats)

        return top_assists    