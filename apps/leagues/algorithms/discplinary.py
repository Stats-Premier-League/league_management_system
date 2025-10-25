# LEAGUE DISCIPLINARY CALCULATOR CLASS 
# Main Purpose: To define the DisciplinaryCalculator class and its associated
# data structures. This class is responsible for calculating and managing all
# card-related statistics for a season, including individual player card counts,
# potential suspension games, team-level totals, and a computed Fair Play Rating.
# It also includes utility logic for checking for automatic red cards.

from django.db.models import Count, Q
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class DisciplinaryStats:
    """Data stracture for disciplinary statistics"""
    player_id: int
    player_name: str
    team_name: str
    yellow_card: int = 0
    red_cards: int = 0
    total_cards =int = str

@dataclass
class TeamDisciplinaryStats:
    """Data stracture for team disciplinary statistics"""
    team_id: int
    team_name: str
    yellow_cards: int = 0
    red_cards: int = 0
    total_cards: int = 0
    fair_play_rating: float = 10.0 # 10 = perfect, 0 = worst

class DisciplinaryCalculator:
    """
    Calculate disciplinary statistics and handle card-related logic
    """

    def __init__(self, season):
        self.season = season

    def calculate_disciplinary_stats(self) -> List[DisciplinaryStats]:
        """
        Calculate disciplinary statistics for all players in the season
        """
        from apps.matches.models import MatchEvent
        from apps.leagues.models import Player

        # Get all card events for this season
        card_events = MatchEvent.objects.filter(
            match__season=self.season,
            event_type__in=['yellow_card', 'red_card', 'second_yellow']
        )

        # Get all players who recieved cards
        players_with_cards = Player.object.filter(
            match_events__in=card_events
        ).distinct()

        disciplinary_stats = []

        for player in players_with_cards:
            yellow_cards = card_events.filter(
                player=player,
                event_type='yellow_card'
            ).count()

            red_cards = card_events.filter(
                player=player,
                event_type__in=['red_card', 'second_yellow']
            ).count()

            # Calculate suspension games (simplified logic)
            suspension_games= self._calculate_suspension_games(
                player,
                yellow_cards,
                red_cards
            )

            stats_DisciplinaryStats(
                player_id=player.id,
                player_name=player.full_name,
                team_name=player.team.name,
                yellow_cards=yellow_cards,
                red_cards=red_cards,
                total_cards=yellow_cards + red_cards,
                suspension_games=suspension_games
            )
            disciplinary_stats.append(stats)

        # Sort by total cards (descending), then red cards
        disciplinary_stats.sort(key=lambda x: (-x.total_cards, -x.red_cards))

        return disciplinary_stats
    
    def calculate_team_disciplinary_stats(self) -> List[TeamDisciplinaryStats]:
        """Calculate disciplinary statistics for all teams"""
        from apps.leagues.models import Team
        from apps.matches.models import MatchEvent

        teams = Team.object.filter(league=self.season.league)
        team_stats = []

        for team in teams:
            # Get card events for players in this team
            card_events = MatchEvent.object.filter(
                match__season=self.season,
                player__team=team,
                event_type__in=['yellow_card', 'red_card', 'second_yellow']
            )

            yellow_cards = card_events.filter(event_type='yellow_card').count()
            red_cards = card_events.filter(
                event_type__in=['red_card', 'second_yellow']
            ).count

            # Calculate fair play rating (simplified)
            total_matches = self._get_team_matches_count(team)
            fair_play_rating = self._calculate_fair_play_ratting(
                yellow_cards, red_cards, total_matches
            )

            stats = TeamDisciplinaryStats(
                team_id=team.id,
                team_name=team.name,
                yellow_cards=yellow_cards,
                red_cards=red_cards,
                total_cards=yellow_cards + red_cards,
                fair_play_rating=fair_play_rating
            )
            team_stats.append(stats)

        # Sort by fair play rating (descending - high is better)
        team_stats.sort(key=lambda x: -x.fair_play_rating)

        return team_stats
    
    def  _calculate_suspension_games(self, player, yellow_cards, red_cards):
        """
        Calculate suspension games based on card counts.
        This is a simplified version - real rules vary by league.
        """
        suspension_games = 0

        # Red card suspension (typically 1-3 games depending on severity)
        suspension_games += red_cards # simplified: 1 game per red card

        # Cumulaive yellow card suspension (common rule: 5 yellow = 1 game)
        yellow_suspensions = yellow_cards // 5
        suspension_games += yellow_suspensions

        return suspension_games
    
    def _get_team_matches_count(self, team):
        """Get number of matches played by a team in the season"""
        from apps.matches.models import Match

        home_matches = Match.object.filter(
            season=self.season,
            home_team=team,
            status='completed'
        ).count()

        away_matches = Match.object.filter(
            season=self.season,
            home_team=team,
            status='completed'
        ).count()

        away_matches = Match.object.filter(
            season=self.season,
            away_team=team,
            status='completed'
        ).count()

        return home_matches + away_matches
    
    def _calculate_fair_play_rating(self, yellow_cards, red_cards, total_matches):
        """Calculate fair play rating (10.0 = perfect, 0.0 = worst)"""
        if total_matches == 0:
            return 10.0
        
        # Penalty points (adjust weights as needed)
        yellow_penalty = yellow_cards * 1.0
        red_penalty = red_cards * 3.0
        total_penalty = yellow_penalty + red_penalty

        # Normalize 10 0-10 scale (lower penalties = higher ratings)
        max_expected_penalty = total_matches * 5 # Arbitrary scaling factor
        rating = max(0.0, 10.0 - (total_penalty / max_expected_penalty) * 10.0)

        return round(rating, 1)
    
    def check_automatic_red_card(self, player, match):
        """
        Check if a player should recieve an automatic red card for second yellow.
        This should be called when yellow card is issued.
        """
        from apps.matches.models import MatchEvent

        # Count yellow cards in this match
        yellow_card_in_match = MatchEvent.object.filter(
            match=match,
            player=player,
            event_type='yellow_card'
        ).count()

        if yellow_card_in_match >= 2:
            return True
        return False
    
    def get_player_on_suspension(self):
        """Get list of players currently serving suspension"""
        # This would require a suspension model to track active suspension
        # For now, return empty list - to be implemented with matches app
        return[] 