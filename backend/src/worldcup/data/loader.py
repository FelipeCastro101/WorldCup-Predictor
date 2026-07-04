# this file takes the raw kaggle csv and turns it into our Match objects.
# it also drops any match involving a non-FIFA team (micronations, ConIFA
# teams, etc) since those can never actually appear in a World Cup, and
# any match with missing/incomplete score data.

import pandas as pd

from worldcup.data.schema import Match
from worldcup.data.team_codes import get_team_code, is_resolvable


def load_matches(csv_path: str) -> list[Match]:
    """reads the raw results csv and returns a list of clean Match objects.
    skips rows where either team isn't a real FIFA-affiliated team, or
    where score data is missing/incomplete."""

    df = pd.read_csv(csv_path)

    # build a lookup ONCE per unique team name instead of recomputing
    # pycountry's fuzzy search on every single row
    unique_teams = set(df["home_team"]) | set(df["away_team"])
    team_lookup = {
        team: (is_resolvable(team), get_team_code(team) if is_resolvable(team) else None)
        for team in unique_teams
    }

    matches = []
    skipped_non_fifa = 0
    skipped_missing_data = 0

    for i, row in df.iterrows():
        home = row["home_team"]
        away = row["away_team"]

        home_resolvable, home_code = team_lookup[home]
        away_resolvable, away_code = team_lookup[away]

        if not home_resolvable or not away_resolvable:
            skipped_non_fifa += 1
            continue

        if pd.isna(row["home_score"]) or pd.isna(row["away_score"]):
            skipped_missing_data += 1
            continue

        match = Match(
            match_id=f"match_{i}",
            date=row["date"],
            tournament=row["tournament"],
            team_a_id=home_code,
            team_b_id=away_code,
            team_a_score=int(row["home_score"]),
            team_b_score=int(row["away_score"]),
            neutral_venue=bool(row["neutral"]),
            stage=None,
        )
        matches.append(match)

    print(f"Loaded {len(matches)} matches")
    print(f"Skipped {skipped_non_fifa} (non-FIFA teams), {skipped_missing_data} (missing score data)")
    return matches
