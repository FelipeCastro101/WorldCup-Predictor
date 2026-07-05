# this file computes "recent form" for each team - basically, how have they
# been doing lately, as opposed to elo which reflects their whole history.
#
# it reuses the elo_history dataframe we already built for opponent strength,
# the "recent_elo_change" signal, but pulls the ACTUAL match result (not the
# elo delta) for win/draw/loss counts - a draw against a stronger team can
# produce a positive elo delta, so we can't infer result from delta sign.

import pandas as pd

FORM_WINDOW = 5  # how many recent matches count as "recent form"


def _team_match_log(elo_df: pd.DataFrame, team_id: str) -> pd.DataFrame:
    """pulls every match a given team played (whether they were team_a or
    team_b in that row), normalized into a consistent view: this team's
    elo_before/elo_after and actual result, regardless of which side they
    were on. actual_result is always from THIS team's perspective:
    1 = win, 0.5 = draw, 0 = loss."""

    as_a = elo_df[elo_df["team_a_id"] == team_id].copy()
    as_a["team_elo_before"] = as_a["team_a_elo_before"]
    as_a["team_elo_after"] = as_a["team_a_elo_after"]
    as_a["actual_result"] = as_a["actual_score_a"]

    as_b = elo_df[elo_df["team_b_id"] == team_id].copy()
    as_b["team_elo_before"] = as_b["team_b_elo_before"]
    as_b["team_elo_after"] = as_b["team_b_elo_after"]
    as_b["actual_result"] = 1 - as_b["actual_score_a"]  # flip perspective

    combined = pd.concat([as_a, as_b])
    return combined.sort_values("date")


def compute_recent_form(elo_df: pd.DataFrame) -> pd.DataFrame:
    """returns a dataframe with one row per (match, team) pair, containing
    that team's recent form going INTO that match: their elo change over
    the last FORM_WINDOW matches, plus real win/draw/loss counts."""

    all_teams = set(elo_df["team_a_id"]) | set(elo_df["team_b_id"])
    records = []

    for team_id in all_teams:
        log = _team_match_log(elo_df, team_id)

        elo_deltas = (log["team_elo_after"] - log["team_elo_before"]).tolist()
        results = log["actual_result"].tolist()
        match_ids = log["match_id"].tolist()

        for i in range(len(log)):
            # only look BACKWARD - matches strictly before this one
            window_deltas = elo_deltas[max(0, i - FORM_WINDOW):i]
            window_results = results[max(0, i - FORM_WINDOW):i]

            wins = sum(1 for r in window_results if r == 1)
            draws = sum(1 for r in window_results if r == 0.5)
            losses = sum(1 for r in window_results if r == 0)

            records.append({
                "match_id": match_ids[i],
                "team_id": team_id,
                "recent_elo_change": sum(window_deltas),
                "recent_wins": wins,
                "recent_draws": draws,
                "recent_losses": losses,
                "matches_in_window": len(window_deltas),
            })

    return pd.DataFrame(records)