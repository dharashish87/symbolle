from flask import Flask, render_template, request, redirect, url_for
import random
from datetime import datetime

app = Flask(__name__)

# Define the set of symbols
symbols = ['*', '#', '@', '$', '%', '&', '^', '!', '?', '+']

# In-memory game state
game_state = {}

@app.route('/', methods=['GET', 'POST'])
def symbolle():
    global game_state

    # Initialize or load lives
    lives = int(game_state.get('lives', 3))
    last_reset = game_state.get('last_reset', None)
    today = datetime.now().strftime('%Y-%m-%d')
    if last_reset != today:
        lives = 3
        game_state['lives'] = lives
        game_state['last_reset'] = today

    # Check if player can continue playing
    if lives == 0:
        game_over = True
        message = "No lives left today. Come back tomorrow!"
        attempts = 0
        guesses = []
        feedback = []
    else:
        # Load or initialize game state
        hidden_sequence = game_state.get('hidden_sequence', None)
        if hidden_sequence is None:
            hidden_sequence = ''.join(random.choices(symbols, k=5))
            game_state['hidden_sequence'] = hidden_sequence
            game_state['attempts'] = 5
            game_state['guesses'] = []
            game_state['feedback'] = []
            game_state['game_over'] = False
            game_state['message'] = ''

        # Retrieve current game state
        attempts = int(game_state['attempts'])
        guesses = game_state['guesses']
        feedback = game_state['feedback']
        game_over = game_state['game_over']
        message = game_state.get('message', '')

        # Handle guess submission
        if request.method == 'POST' and not game_over:
            guess = request.form.get('guess', '').strip()
            if len(guess) == 5 and all(char in symbols for char in guess):
                # Calculate feedback based on fixed sequence
                feedback_for_guess = [guess[i] == hidden_sequence[i] for i in range(5)]
                guesses.append(guess)
                feedback.append(feedback_for_guess)
                game_state['guesses'] = guesses
                game_state['feedback'] = feedback

                # Check win condition
                if all(feedback_for_guess):
                    game_over = True
                    message = "Congratulations! You guessed it right!"
                    game_state['game_over'] = True
                    game_state['message'] = message
                else:
                    # Decrement attempts
                    attempts -= 1
                    game_state['attempts'] = attempts
                    if attempts <= 0:
                        lives -= 1
                        game_over = True
                        message = f"Failed to guess. Lives left: {lives}"
                        game_state['lives'] = lives
                        game_state['game_over'] = True
                        game_state['message'] = message

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
    global game_state
    # Reset game state
    game_state.pop('hidden_sequence', None)
    game_state.pop('attempts', None)
    game_state.pop('guesses', None)
    game_state.pop('feedback', None)
    game_state.pop('game_over', None)
    game_state.pop('message', None)
    return redirect(url_for('symbolle'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)