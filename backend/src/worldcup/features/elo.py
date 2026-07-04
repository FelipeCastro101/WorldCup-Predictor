# this file calculates each team's elo rating over time, based on match history.
# elo is a running number per team that goes up after wins, down after losses.
# the amount it moves depends on three things:
#   1. how "surprising" the result was (upsets move the needle more)
#   2. how many matches the team has already played (new teams are less
#      certain, so their rating should swing more until it stabilizes)
#   3. the goal difference (a blowout is stronger evidence than a close win)

from worldcup.data.schema import Match

STARTING_ELO = 1500.0

# controls how fast/slow ratings move based on match experience
K_MAX = 40.0     # new team, rating barely trusted yet, moves fast
K_MIN = 20.0     # established team, rating well-earned, moves slow
DECAY_RATE = 10  # controls how quickly K drops from max to min as matches pile up


def expected_score(rating_a: float, rating_b: float) -> float:
    """given two elo ratings, what's the probability team a wins?
    equal ratings = 0.5 (coin flip). bigger gap = closer to 0 or 1."""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))


def k_factor(matches_played: int) -> float:
    """returns how much a team's rating should move, based on how many
    matches they've played so far. brand new teams (matches_played=0) get
    K_MAX. as matches_played grows, K smoothly drops toward K_MIN."""
    return K_MIN + (K_MAX - K_MIN) / (1 + matches_played / DECAY_RATE)


def goal_diff_multiplier(goal_diff: int) -> float:
    """a blowout win is stronger evidence of a quality gap than a narrow
    one, so we scale the rating change up as goal difference grows.
    a 1-goal margin doesn't get boosted at all - only bigger margins do."""
    if goal_diff <= 1:
        return 1.0
    elif goal_diff == 2:
        return 1.5
    else:
        return (11 + goal_diff) / 8


def update_elo(
    rating_a: float,
    rating_b: float,
    actual_score_a: float,
    matches_played_a: int,
    matches_played_b: int,
    goal_diff: int = 1,
) -> tuple[float, float]:
    """given both teams' current ratings, match counts, the actual result
    (1=win, 0.5=draw, 0=loss, from team a's perspective), and the goal
    difference of the match, returns their new ratings. each team uses its
    OWN k-factor (based on its own experience), and both get scaled by the
    same goal-difference multiplier (a blowout affects both teams equally)."""

    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a

    actual_score_b = 1 - actual_score_a

    k_a = k_factor(matches_played_a)
    k_b = k_factor(matches_played_b)

    multiplier = goal_diff_multiplier(goal_diff)

    new_rating_a = rating_a + k_a * multiplier * (actual_score_a - expected_a)
    new_rating_b = rating_b + k_b * multiplier * (actual_score_b - expected_b)

    return new_rating_a, new_rating_b