# this file runs the elo math (from elo.py) across real match history.
# it walks through every match in chronological order, keeping a running
# elo rating + match count per team, and records each team's elo BEFORE
# the match happened - that's the actual feature a model will use later,
# since we want "how strong was this team going into the match", not
# their final rating after everything already happened.

import pandas as pd

from worldcup.data.loader import load_matches
from worldcup.features.elo import STARTING_ELO, update_elo


def compute_elo_history(csv_path: str) -> pd.DataFrame:
    """returns a dataframe with one row per match, including each team's
    elo rating going INTO that match (the useful feature) plus their
    elo AFTER (just for sanity-checking/debugging)."""

    matches = load_matches(csv_path)

    # matches from load_matches aren't guaranteed sorted - elo is inherently
    # sequential, so this order matters a lot. sort oldest first.
    matches.sort(key=lambda m: m.date)

    ratings = {}       # team_id -> current elo
    match_counts = {}  # team_id -> how many matches they've played so far

    records = []

    for match in matches:
        team_a = match.team_a_id
        team_b = match.team_b_id

        # if we've never seen this team before, they start at STARTING_ELO
        # with 0 matches played
        rating_a = ratings.get(team_a, STARTING_ELO)
        rating_b = ratings.get(team_b, STARTING_ELO)
        played_a = match_counts.get(team_a, 0)
        played_b = match_counts.get(team_b, 0)

        # figure out the actual result from team a's perspective
        if match.team_a_score > match.team_b_score:
            actual_score_a = 1.0
        elif match.team_a_score < match.team_b_score:
            actual_score_a = 0.0
        else:
            actual_score_a = 0.5

        goal_diff = abs(match.team_a_score - match.team_b_score)

        new_rating_a, new_rating_b = update_elo(
            rating_a, rating_b, actual_score_a, played_a, played_b, goal_diff
        )

        records.append({
            "match_id": match.match_id,
            "date": match.date,
            "team_a_id": team_a,
            "team_b_id": team_b,
            "team_a_elo_before": rating_a,
            "team_b_elo_before": rating_b,
            "team_a_elo_after": new_rating_a,
            "team_b_elo_after": new_rating_b,
            "actual_score_a": actual_score_a,
        })

        # update state for next time we see these teams
        ratings[team_a] = new_rating_a
        ratings[team_b] = new_rating_b
        match_counts[team_a] = played_a + 1
        match_counts[team_b] = played_b + 1

    return pd.DataFrame(records)