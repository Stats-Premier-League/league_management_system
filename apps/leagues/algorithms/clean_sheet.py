# LEAGUE CLEAN SHEET CALCULATOR CLASS 
# Main Purpose: To define the CleanSheetCalculator class and its associated
# data structures. This class is specialized in computing defensive statistics,
# primarily the number of clean sheets (matches played without conceding a goal)
# for both the teams and individual goalkeepers within a given season.
# It also includes a utility function to mark clean sheets on a match record itself.

from django.db.models import Q, Count
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CleanSheetStats:
    """Data structure for clean sheet statistics."""
    team_id: int
    team_name: str
    clean_sheets: int = 0
    matches_played: int = 0
    clean_sheet_percentage: float = 0.0

@dataclass
class GoalKeeperCleanSheetStats:
    """Data structure for goalkeeper-specific clean sheet."""
    player_id: int
    player_name: str
    team_name: str
    clean_sheets: int = 0
    matches_played: int = 0

class CleanSheetCalculator:
    """
    Calculate clean sheets statistics for teams and goalkeepers.
    A clean sheet is awarded when a team doesn't concede any goals in a match
    """
    
    def __init__(self, season):
        self.season = season

    def calculate_clean_sheets(self) -> List[CleanSheetStats]:
        """
        Calculate clean sheet statistics for all teams in the season.
        """
        from apps.leagues.models import Team
        from apps.matches.models import Match

        teams = Team.objects.filter(league=self.season.league)
        clean_sheet_stats = []

        for team in teams:
            # Get all matches where the team played (home or away)
            home_matches = Match.objects.filter(
                season=self.season,
                home_team=team,
                status='completed'
            )

            away_matches = Match.objects.filter(
                season=self.season,
                away_team=team,
                status='completed'
            )

            # Calculate clean sheets
            home_clean_sheets = home_matches.filter(home_clean_sheet=True).count()
            away_clean_sheets = away_matches.filter(away_clean_sheet=True).count()

            total_clean_sheets = home_clean_sheets + away_clean_sheets
            total_matches = home_matches.count() + away_matches.count()

            # Calculate percentage
            clean_sheet_percentage = 0.0
            if total_matches > 0:
                clean_sheet_percentage = round((total_clean_sheets / total_matches) * 100, 1)

            stats = CleanSheetStats(
                team_id=team.id,
                team_name=team.name,
                clean_sheets=total_clean_sheets,
                matches_played=total_matches,
                clean_sheet_percentage=clean_sheet_percentage
            )
            clean_sheet_stats.append(stats)

        # Sort by clean sheets (descending), then by percentage
        clean_sheet_stats.sort(key=lambda x: (-x.clean_sheets, -x.clean_sheet_percentage))

        return clean_sheet_stats

    def calculate_goalkeeper_clean_sheets(self) -> List[GoalKeeperCleanSheetStats]:
        """
        Calculate clean sheet for statistics for goalkeepers.
        More complex - requires racking which goalkeeper was playing during the goals.
        """
        from apps.leagues.models import Player
        from apps.matches.models import MatchEvent

        # Get all goalkeepers in the league
        goalkeepers = Player.objects.filter(
            team__league=self.season.league,
            is_gaolkeeper=True
        )

        gk_stats = []

        for gk in goalkeepers:
            # This is a simplified version - in reality, youd need to check
            # if the goalkeeper was on the pitch when gaols were conceded

            # Get matches where this goalkeeper's team played
            from apps.matches.models import Match
            team_matches = Match.objects.filter(
                season=self.season,
                status='completed'
            ).filter(
                Q(home_team=gk.team) | Q(away_team=gk.team)
            )

            clean_sheets = 0
            goals_against = 0

            for match in team_matches:
                # Determine if this was a clean sheet for the goalkeeper's team
                if match.home_team == gk.team and match.away_score == 0:
                    clean_sheets += 1
                elif match.away_team == gk.team and match.home_score == 0:
                    clean_sheets += 1

                # Count goals against: reminder to check line 129 
                if match.home_team == gk.team:
                    goals_against += match.away_score
                else:
                    goals_against += match.home_score

            stats = GoalKeeperCleanSheetStats(
                player_id=gk.id,
                player_name=gk.full_name,
                team_name=gk.team.name,
                clean_sheets=clean_sheets,
                matches_played=team_matches.count(),
                goals_against=goals_against
            )
            gk_stats.append(stats)

        # Sort by clean sheets (descending)
        gk_stats.sort(key=lambda x: (-x.clean_sheets, x.goals_against))

        return gk_stats
    
    def update_match_clean_sheet(self, match):
        """
        Update clean sheets flag for a specific match.
        This should be called when match results are finalized.
        """
        # Home team clean sheet
        match.home_clean_sheet = (match.away_score == 0)
        # Away team clean sheet
        match.away_clean_sheet = (match.home_score == 0)

        match.save(update_fields=['home_clean_sheet', 'away_clean_sheet'])