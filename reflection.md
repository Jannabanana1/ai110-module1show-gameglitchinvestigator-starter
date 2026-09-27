# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
* The game looked pretty normal and worked as it should. 
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").
  * One bug I saw was that the history of my input did not show right after input. 
  Location: st.session_state.history.append(guess_int)
  app.py
  * Another issue is that it says -5 but gives you score of 85 if one input is wrong. Therefore, the points reduced and the total points given don't match. 
  Location: update_score method in logic_utils.py
  * History shows that the attempt starts at 0 although it should start at 1
  Location: st.session_state.history.append(guess_int) app.py
**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|6 | Should be -15 and Score = 85 |Score=85 but -5 points  |Location: update_score method in logic_utils.py |
|5 | Should add input history |No history till second input |The error is in Location: st.session_state.history.append(guess_int) app.py|
|10 |Expected to show attempt 1: 10 |Actual: attempt 0: 10 | Location: st.session_state.history.append(guess_int)
  app.py|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
*Claude
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
* It changed the code so that attempts made is updated right away rather than lagging behind each attempt. 
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
* One example is when I asked it to change how the scores were calculated. It ends a normal game at score of -40 when all attempts are made, but it does not make sense to have a negative score. 
---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
* I read over what claude changed and I re-started the game to make sure it worked the way it should. 
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  * I ran pytest on attempts made by using inputs to test it and made sure it passed.
- Did AI help you design or understand any tests? How?
* Yes, it explained what it did when it changed things very thoroughly. 
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---Streamlit reruns your whole script whenever the user interacts with the app, and st.session_state lets you preserve information across those reruns.

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
* Using claude code to figure out how to debug and creating pytests using AI claude code
 
- What is one thing you would do differently next time you work with AI on a coding task?
* I will probably ask AI to explain more of the code so that I get the full context
- In one or two sentences, describe how this project changed the way you think about AI generated code.
* This project made me realize that AI can be helpful since it makes the process much faster. However, it can also be harmful if it makes a mistake that is not caught by the developer.