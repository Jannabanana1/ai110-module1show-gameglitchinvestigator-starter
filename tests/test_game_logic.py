from logic_utils import attempts_remaining, check_guess, record_guess

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
