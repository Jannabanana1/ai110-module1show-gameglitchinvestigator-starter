"""Pure game logic for the number guessing game.

Nothing in here touches Streamlit, so every function can be unit tested
directly with pytest.
"""

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 50),
}

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}

DEFAULT_DIFFICULTY = "Normal"


def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES[DEFAULT_DIFFICULTY])


def get_attempt_limit(difficulty: str):
    """Return how many guesses the player gets for a given difficulty."""
    return ATTEMPT_LIMITS.get(difficulty, ATTEMPT_LIMITS[DEFAULT_DIFFICULTY])


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    text = raw.strip()
    if text == "":
        return False, None, "Enter a guess."

    try:
        value = int(text)
    except ValueError:
        return False, None, f"'{raw}' is not a whole number."

    if low is not None and high is not None and not (low <= value <= high):
        return False, None, f"Guess must be between {low} and {high}."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret.

    Returns one of: "Win", "Too High", "Too Low"
    """
    guess = int(guess)
    secret = int(secret)

    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def hint_for_outcome(outcome: str):
    """Return the player-facing message for an outcome from check_guess."""
    messages = {
        "Win": "🎉 Correct!",
        "Too High": "📉 Too high — go LOWER!",
        "Too Low": "📈 Too low — go HIGHER!",
    }
    return messages.get(outcome, "")


def update_score(current_score: int, outcome: str, attempt_number: int):
    """
    Update score based on outcome and attempt number.

    A win pays 100 points minus 5 for each guess already missed, so a win on
    attempt N is worth 100 - 5 * (N - 1): 100, 95, 90, 85 and so on, never
    below zero. Each miss costs 5 points, charged exactly once.

    Two things this shape is deliberately guarding:

    1. The bonus used to decay by 10 per attempt ON TOP of a -5 deducted at
       each miss, which charged every miss twice -- a win on attempt 2 paid
       85 rather than 95.
    2. A miss does not deduct from the running score, because the score is
       floored at zero and starts at zero: a running deduction would be
       clamped away immediately and cost the player nothing. Charging the
       miss against the win bonus is what makes the 5 points real.
    """
    if outcome == "Win":
        return max(0, current_score + 100 - 5 * (attempt_number - 1))

    if outcome in ("Too High", "Too Low"):
        # Already paid for by the smaller win bonus above.
        return max(0, current_score)

    return max(0, current_score)


def attempts_remaining(attempt_limit: int, attempts_used: int):
    """Return how many guesses are left, floored at zero.

    `attempts_used` counts guesses already completed, so callers must pass the
    count *after* the current guess has been recorded — otherwise the number
    shown to the player lags one turn behind.
    """
    return max(0, attempt_limit - attempts_used)


def record_guess(state: dict, raw: str, low: int, high: int, attempt_limit: int):
    """Apply one submitted guess and return the resulting game state.

    `state` needs the keys: attempts, score, history, secret, status. The
    returned dict has those keys updated plus "messages", a list of
    (kind, text) pairs for the UI to render. The input dict is left untouched.

    Invalid input is rejected without consuming an attempt.
    """
    new_state = dict(state)
    new_state["history"] = list(state["history"])
    messages = []
    new_state["messages"] = messages

    ok, guess, error = parse_guess(raw, low, high)
    if not ok:
        # A bad input is not a real guess, so it does not burn an attempt.
        messages.append(("error", error))
        return new_state

    new_state["attempts"] = state["attempts"] + 1
    new_state["history"].append(guess)

    outcome = check_guess(guess, state["secret"])
    new_state["score"] = update_score(
        current_score=state["score"],
        outcome=outcome,
        attempt_number=new_state["attempts"],
    )

    if outcome == "Win":
        new_state["status"] = "won"
        messages.append((
            "success",
            f"You won in {new_state['attempts']} attempts! "
            f"The secret was {state['secret']}. "
            f"Final score: {new_state['score']}",
        ))
        return new_state

    messages.append(("hint", hint_for_outcome(outcome)))

    if attempts_remaining(attempt_limit, new_state["attempts"]) == 0:
        new_state["status"] = "lost"
        messages.append((
            "error",
            f"Out of attempts! The secret was {state['secret']}. "
            f"Score: {new_state['score']}",
        ))

    return new_state
