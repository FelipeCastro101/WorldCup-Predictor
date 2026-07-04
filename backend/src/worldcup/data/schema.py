from datetime import date
from pydantic import BaseModel

# this file is basically the blueprint for our data - just defines what
# a team, match, tournament, etc

class Team(BaseModel):
    team_id: str  # example my favorite team "ARG" messi = goat
    name: str
    confederation: str  # UEFA, CONMEBOL, CAF, AFC, CONCACAF, OFC
    elo_rating: float
    fifa_ranking: int | None = None


class HistoricalPrior(BaseModel):
    team_id: str
    world_cup_wins: int
    world_cup_appearances: int
    round_of_16_appearances: int
    quarterfinal_appearances: int
    semifinal_appearances: int
    final_appearances: int
    historical_elo_avg: float


class Match(BaseModel):
    match_id: str
    date: date
    tournament: str
    team_a_id: str
    team_b_id: str
    team_a_score: int
    team_b_score: int
    neutral_venue: bool
    stage: str | None = None


class Tournament(BaseModel):
    tournament_id: str
    name: str
    year: int
    host_country: str
    format: str


class TournamentEntry(BaseModel):
    tournament_id: str
    team_id: str
    group: str
