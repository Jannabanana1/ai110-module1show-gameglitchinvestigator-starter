import random

import streamlit as st

from logic_utils import (
    attempts_remaining,
    get_attempt_limit,
    get_range_for_difficulty,
    numbered_history,
    record_guess,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game — now debugged.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

low, high = get_range_for_difficulty(difficulty)
attempt_limit = get_attempt_limit(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")


def start_new_game():
    """Reset every piece of game state for the current difficulty."""
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty
    st.session_state.messages = []
    st.session_state.celebrate = False


def handle_submit():
    """Record the pending guess.

    This runs as a button callback, so it finishes before the script reruns.
    Everything below therefore renders state that already includes this guess,
    rather than the previous turn's.
    """
    if st.session_state.status != "playing":
        return

    guess_low, guess_high = get_range_for_difficulty(st.session_state.difficulty)

    result = record_guess(
        {
            "attempts": st.session_state.attempts,
            "score": st.session_state.score,
            "history": st.session_state.history,
            "secret": st.session_state.secret,
            "status": st.session_state.status,
        },
        st.session_state.guess_input,
        guess_low,
        guess_high,
        get_attempt_limit(st.session_state.difficulty),
    )

    st.session_state.attempts = result["attempts"]
    st.session_state.score = result["score"]
    st.session_state.history = result["history"]
    st.session_state.status = result["status"]
    st.session_state.messages = result["messages"]
    st.session_state.celebrate = result["status"] == "won"


# Seed state on first load only, so the secret survives every rerun.
if "secret" not in st.session_state:
    start_new_game()

# Changing difficulty changes the range, so the old secret may be out of bounds.
if st.session_state.difficulty != difficulty:
    start_new_game()

game_over = st.session_state.status != "playing"

st.subheader("Make a guess")

st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempts_remaining(attempt_limit, st.session_state.attempts)}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    # Numbered from 1 so an entry lines up with the attempt that made it.
    st.write("History:", numbered_history(st.session_state.history))

st.text_input("Enter your guess:", key="guess_input", disabled=game_over)

col1, col2, col3 = st.columns(3)
with col1:
    st.button("Submit Guess 🚀", on_click=handle_submit, disabled=game_over)
with col2:
    st.button("New Game 🔁", on_click=start_new_game)
with col3:
    show_hint = st.checkbox("Show hint", value=True)

for kind, text in st.session_state.get("messages", []):
    if kind == "hint":
        if show_hint:
            st.warning(text)
    elif kind == "success":
        st.success(text)
    else:
        st.error(text)

if st.session_state.get("celebrate"):
    st.balloons()
    st.session_state.celebrate = False

if game_over:
    st.caption("Start a new game to play again.")

st.divider()
st.caption("Built by an AI that claimed this code was production-ready.")
