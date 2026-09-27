from logic_utils import (
    attempts_remaining,
    check_guess,
    numbered_history,
    record_guess,
    update_score,
)

NORMAL_LOW, NORMAL_HIGH = 1, 100
NORMAL_LIMIT = 8


def new_state(secret=50, attempts=0, score=0, status="playing"):
    """A fresh game state dict shaped the way record_guess expects."""
    return {
        "attempts": attempts,
        "score": score,
        "history": [],
        "secret": secret,
        "status": status,
    }


def guess(state, raw, limit=NORMAL_LIMIT):
    return record_guess(state, raw, NORMAL_LOW, NORMAL_HIGH, limit)


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# --- Regression tests for the stale "Attempts left" display -----------------
#
# The bug: app.py rendered the attempts counter before the guess had been
# recorded, so the number shown was always one turn behind. The fix moved the
# state change into record_guess, called from a button callback that finishes
# before anything renders. These tests pin the rule that fix depends on -- the
# state returned by record_guess already accounts for the guess just made.


def test_attempts_left_reflects_the_guess_just_made():
    """THE regression test: no one-turn lag after a valid guess."""
    state = new_state()
    assert attempts_remaining(NORMAL_LIMIT, state["attempts"]) == 8

    after = guess(state, "40")

    assert after["attempts"] == 1
    assert attempts_remaining(NORMAL_LIMIT, after["attempts"]) == 7


def test_attempts_left_decreases_on_every_valid_guess():
    state = new_state()
    for expected_left in (7, 6, 5, 4):
        state = guess(state, "40")
        assert attempts_remaining(NORMAL_LIMIT, state["attempts"]) == expected_left


def test_unparseable_input_does_not_consume_an_attempt():
    state = new_state()
    after = guess(state, "banana")

    assert after["attempts"] == 0
    assert attempts_remaining(NORMAL_LIMIT, after["attempts"]) == 8
    assert after["history"] == []


def test_out_of_range_input_does_not_consume_an_attempt():
    state = new_state()
    after = guess(state, "150")

    assert after["attempts"] == 0
    assert attempts_remaining(NORMAL_LIMIT, after["attempts"]) == 8
    assert after["history"] == []


def test_player_gets_every_allowed_attempt():
    """Guarding the old attempts=1 bug, which ended the game one guess early."""
    limit = 3
    state = new_state()

    for _ in range(limit - 1):
        state = guess(state, "40", limit)
        assert state["status"] == "playing"

    state = guess(state, "40", limit)
    assert state["status"] == "lost"
    assert state["attempts"] == limit
    assert attempts_remaining(limit, state["attempts"]) == 0


def test_attempts_remaining_never_goes_negative():
    assert attempts_remaining(5, 7) == 0


def test_record_guess_does_not_mutate_the_state_it_was_given():
    state = new_state()
    guess(state, "40")

    assert state["attempts"] == 0
    assert state["history"] == []


# --- Regression tests for scoring -------------------------------------------
#
# Two bugs lived here.
#
# 1. The double-charged miss. A wrong guess cost 5 points AND shrank the later
#    win bonus by 10, because the bonus decayed with the attempt number. One
#    miss really cost 15, so a win on attempt 2 paid 85 when the docstring
#    promised a 5-point penalty.
# 2. The negative final score. Nothing floored the score, so losing a Normal
#    game ended on -40 while attempts_remaining was already floored at zero.
#
# Fixing both at once forces the shape the code has now: the 5-point charge
# lives in the win bonus, not in a running deduction. A deduction cannot work
# alongside the floor, because the score starts at zero and would clamp back
# to zero on every miss -- costing the player nothing at all.


def test_win_on_first_attempt_scores_100():
    assert update_score(0, "Win", 1) == 100


def test_every_miss_costs_exactly_five():
    """THE regression test: 5 per miss, not the 15 the old bonus decay cost."""
    for attempt_number in range(1, 11):
        expected = 100 - 5 * (attempt_number - 1)
        assert update_score(0, "Win", attempt_number) == expected


def test_a_miss_does_not_move_the_running_score():
    for outcome in ("Too High", "Too Low"):
        assert update_score(0, outcome, 1) == 0
        assert update_score(40, outcome, 3) == 40


def test_score_never_goes_below_zero():
    """A win so late its bonus is spent still pays nothing, never a debt."""
    assert update_score(0, "Win", 30) == 0
    assert update_score(-10, "Too High", 1) == 0


def test_unknown_outcome_leaves_the_score_alone():
    assert update_score(42, "Sideways", 1) == 42


def test_full_game_win_costs_five_per_miss():
    """A win on attempt N is worth 100 - 5 * (N - 1), driven through the game."""
    for attempt_number, expected in [(1, 100), (2, 95), (3, 90), (4, 85)]:
        state = new_state()
        for _ in range(attempt_number - 1):
            state = guess(state, "40")
        state = guess(state, "50")

        assert state["status"] == "won"
        assert state["attempts"] == attempt_number
        assert state["score"] == expected


def test_losing_a_full_game_bottoms_out_at_zero():
    """The old code finished a lost Normal game on -40."""
    state = new_state()
    for _ in range(NORMAL_LIMIT):
        state = guess(state, "40")

    assert state["status"] == "lost"
    assert state["score"] == 0


def test_rejected_input_does_not_change_the_score():
    state = new_state(score=95)

    assert guess(state, "banana")["score"] == 95
    assert guess(state, "150")["score"] == 95


# --- Regression tests for the 0-indexed history display ---------------------
#
# The bug: app.py handed the raw history list straight to st.write, so the
# viewer labeled the entries 0, 1, 2. Every other count in the game starts at
# 1 -- record_guess sets attempts to 1 after the first guess -- so the first
# guess was shown as entry 0 of attempt 1. numbered_history keys the guesses
# by attempt number instead, and these tests pin that alignment.


def test_history_is_numbered_from_one():
    """THE regression test: the first guess is entry 1, never entry 0."""
    numbered = numbered_history([42, 17, 30])

    assert numbered == {1: 42, 2: 17, 3: 30}
    assert 0 not in numbered
    assert min(numbered) == 1


def test_history_key_matches_the_attempt_that_made_the_guess():
    """Entry N is the guess from attempt N, driven through the real game."""
    state = new_state()
    for raw in ("40", "45", "48"):
        state = guess(state, raw)
        numbered = numbered_history(state["history"])

        # The guess just made is filed under the attempt count it produced.
        assert numbered[state["attempts"]] == int(raw)

    assert numbered_history(state["history"]) == {1: 40, 2: 45, 3: 48}


def test_empty_history_is_numbered_without_error():
    assert numbered_history([]) == {}


def test_rejected_guess_does_not_take_a_history_number():
    """A bad input burns no attempt, so it must not shift the numbering."""
    state = guess(new_state(), "40")
    state = guess(state, "banana")
    state = guess(state, "45")

    assert numbered_history(state["history"]) == {1: 40, 2: 45}


def test_numbered_history_does_not_mutate_the_history_it_was_given():
    history = [42, 17]
    numbered_history(history)

    assert history == [42, 17]
