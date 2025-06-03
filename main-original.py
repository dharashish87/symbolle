from flask import Flask, render_template, request, redirect, url_for
from replit import db
import random
from datetime import datetime

app = Flask(__name__)

# Define the set of symbols
symbols = ['*', '#', '@', '$', '%', '&', '^', '!', '?', '+']

@app.route('/', methods=['GET', 'POST'])
def symbolle():
    # Load and manage lives
    lives = int(db.get('lives', '3'))
    last_reset = db.get('last_reset', None)
    today = datetime.now().strftime('%Y-%m-%d')
    if last_reset != today:
        lives = 3
        db['lives'] = str(lives)
        db['last_reset'] = today

    # Check if player can continue playing
    if lives == 0:
        game_over = True
        message = "No lives left today. Come back tomorrow!"
        attempts = 0
        guesses = []
        feedback = []
    else:
        # Load or initialize game state
        hidden_sequence = db.get('hidden_sequence', None)
        if hidden_sequence is None:
            hidden_sequence = ''.join(random.choices(symbols, k=5))
            db['hidden_sequence'] = hidden_sequence
            db['attempts'] = '5'
            db['guesses'] = []
            db['feedback'] = []
            db['game_over'] = 'False'
            db['message'] = ''

        # Retrieve current game state
        attempts = int(db['attempts'])
        guesses = db['guesses']
        feedback = db['feedback']
        game_over = db['game_over'] == 'True'
        message = db.get('message', '')

        # Handle guess submission
        if request.method == 'POST' and not game_over:
            guess = request.form.get('guess', '').strip()
            if len(guess) == 5 and all(char in symbols for char in guess):
                # Calculate feedback based on fixed sequence
                feedback_for_guess = [guess[i] == hidden_sequence[i] for i in range(5)]
                guesses.append(guess)
                feedback.append(feedback_for_guess)
                db['guesses'] = guesses
                db['feedback'] = feedback

                # Check win condition
                if all(feedback_for_guess):
                    game_over = True
                    message = "Congratulations! You guessed it right!"
                    db['game_over'] = 'True'
                    db['message'] = message
                else:
                    # Decrement attempts
                    attempts -= 1
                    db['attempts'] = str(attempts)
                    if attempts <= 0:
                        lives -= 1
                        game_over = True
                        message = f"Failed to guess. Lives left: {lives}"
                        db['lives'] = str(lives)
                        db['game_over'] = 'True'
                        db['message'] = message

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
    db.pop('hidden_sequence', None)
    db.pop('attempts', None)
    db.pop('guesses', None)
    db.pop('feedback', None)
    db.pop('game_over', None)
    db.pop('message', None)
    return redirect(url_for('symbolle'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)