from flask import Flask, render_template, request, redirect, url_for
import random
from datetime import datetime
import json
import os

app = Flask(__name__)

# Define the set of symbols
symbols = ['*', '#', '@', '$', '%', '&', '^', '!', '?', '+']

# File to store game state
STATE_FILE = 'game_state.json'

# Helper functions to manage game state with JSON
def load_game_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_game_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

@app.route('/', methods=['GET', 'POST'])
def symbolle():
    # Load game state from JSON
    state = load_game_state()

    # Initialize or load lives
    lives = int(state.get('lives', 3))
    last_reset = state.get('last_reset', None)
    today = datetime.now().strftime('%Y-%m-%d')
    if last_reset != today:
        lives = 3
        state['lives'] = lives
        state['last_reset'] = today
        save_game_state(state)

    # Check if player can continue playing
    if lives == 0:
        game_over = True
        message = "No lives left today. Come back tomorrow!"
        attempts = 0
        guesses = []
        feedback = []
    else:
        # Load or initialize game state
        hidden_sequence = state.get('hidden_sequence', None)
        if hidden_sequence is None:
            hidden_sequence = ''.join(random.choices(symbols, k=5))
            state['hidden_sequence'] = hidden_sequence
            state['attempts'] = 5
            state['guesses'] = []
            state['feedback'] = []
            state['game_over'] = False
            state['message'] = ''
            save_game_state(state)

        # Retrieve current game state
        attempts = int(state['attempts'])
        guesses = state['guesses']
        feedback = state['feedback']
        game_over = state['game_over']
        message = state.get('message', '')

        # Handle guess submission
        if request.method == 'POST' and not game_over:
            guess = request.form.get('guess', '').strip()
            if len(guess) == 5 and all(char in symbols for char in guess):
                # Calculate feedback based on fixed sequence
                feedback_for_guess = [guess[i] == hidden_sequence[i] for i in range(5)]
                guesses.append(guess)
                feedback.append(feedback_for_guess)
                state['guesses'] = guesses
                state['feedback'] = feedback

                # Check win condition
                if all(feedback_for_guess):
                    game_over = True
                    message = "Congratulations! You guessed it right!"
                    state['game_over'] = True
                    state['message'] = message
                else:
                    # Decrement attempts
                    attempts -= 1
                    state['attempts'] = attempts
                    if attempts <= 0:
                        lives -= 1
                        game_over = True
                        message = f"Failed to guess. Lives left: {lives}"
                        state['lives'] = lives
                        state['game_over'] = True
                        state['message'] = message
                save_game_state(state)

    # Render the game page
    return render_template('symbolle.html', 
                           symbols=symbols, 
                           lives=lives, 
                           attempts=attempts if not game_over else 0, 
                           guesses=guesses, 
                           feedback=feedback, 
                           game_over=game_over, 
                           message=message)

@app.route('/new_game', methods=['POST'])
def new_game():
    # Reset game state
    state = load_game_state()
    state.pop('hidden_sequence', None)
    state.pop('attempts', None)
    state.pop('guesses', None)
    state.pop('feedback', None)
    state.pop('game_over', None)
    state.pop('message', None)
    save_game_state(state)
    return redirect(url_for('symbolle'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)