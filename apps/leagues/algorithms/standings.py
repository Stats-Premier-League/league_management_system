# LEAGUE STANDINGS CALCULATOR CLASS 
# Main Purpose: To define the StandingsCalculator class and the associated
# TeamStanding data structure. This class performs the complex, iterative
# logic required to calculate and compile the official league table (or standings)
# for a given season based on the results of all completed matches, applying the
# correct points rules and tie-breakers.

from django.db import models
from django.db.models import Q, F,Count, Sum, Case, When, IntegerField
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class TeamStanding:
    """
    Data stracture for team standings.
    """
    team_id: int
    team_name: str
    matches_played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goal_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    form: List[str] = None # Last 5 matches ['w', 'D', 'L', 'W', 'W']

    def __post__init__(self):
        if self.form is None:
            self.form = []

class StandingsCalculator:
    """
    Calculate league standings based on match results.
    """

    def calculate_standings(self) -> List[TeamStanding]:
        """
        Calculate current standings for the season.
        Return sorted lists of TeamStandings objects.
        """
        teams = self.league.teams.all()
        standings_map = {}

        # Initialize standing for all teams
        for team in teams:
            standings_map[team.id] = TeamStanding(
                team_id=team.id,
                team_name=team.name
            )

        # Get all completed matches for this season
        from apps.matches.models import Match # Next will be this

        matches = Match.objects.filter(
            season=self.season,
            status='completed'
        ).select_related('home_team', 'away_team')

        # Process each match
        for match in matches:
            self._process_match_result(match, standings_map)

        # Calculate goaldifference and sort
        standings = list(standings_map.values())

        for standing in standings:
            standing.goal_difference = standing.goal_for - standing.goals_against

        # Sort by points, goal difference, goal for
        standings.sort(key=lambda x: (
            -x.points, # Descending
            -x.goal_difference, # Descending
            -x.goals_for, # Descending
            x.team_name # Ascending by team name 
        ))

        return standings

    def _process_match_result(self, match, standings_map: Dict[int, TeamStanding]):
        """
        Update standings based on single match result.
        """
        home_standig = standings_map[match.home_team.id]
        away_standing = standings_map[match.away_team.id]

        # Update matches played
        home_standing.matches_played += 1
        away_standing.matches_played += 1

        # Update goals
        home_standing.goals_for += match.home_score
        home_standing.goals_against += match.away_score
        away_standing.goals_for += match.away_score
        away_standing.goals_against += match.home_score

        # Determine results and update points
        if match.home_score > match.away_score:
            # Home win
            home_standing.wins += 1
            away_standing.losses += 1
            home_standing.points += self.season.actual_points_per_win
            home_standing.from.append('W')
            home_standing.form.append('L')

        elif match.home_score < match.away_score:
            # Away win
            away_standing.wins += 1
            home_standing.losses += 1
            away_standing.points += self.season.actual_points_per_win
            home_standing.form.append('L')
            away_standing.form.append('W')

        else:
            # Draw
            home_standig.draw += 1
            away_standing.draws += 1
            home_standing.points += self.season.actual_points_per_draw
            home_standing.points += self.season.actual_points_per_draw
            home_standing.form.append('D')
            away_standing.form.append('D')

        # Keep only last 5 matches
        home_standing.form = home_standing.form[-5:]
        away_standing.form = away_standing.form[-5:] 