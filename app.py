from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Game constants
BOARD_SIZE = 12
EMPTY = 0
RED = 1
BLUE = 2

def create_board():
    """Creates an empty game board."""
    return np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

def drop_piece(board, row, col, piece):
    """Drops a piece in the specified column."""
    board[row][col] = piece

def is_valid_location(board, col):
    """Checks if a column is a valid location to drop a piece."""
    return board[BOARD_SIZE - 1][col] == 0

def get_next_open_row(board, col):
    """Gets the next open row in a column."""
    for r in range(BOARD_SIZE):
        if board[r][col] == 0:
            return r
    return None

def winning_move(board, piece):
    """Checks if a player has a winning move."""
    # Check horizontal locations
    for c in range(BOARD_SIZE - 3):
        for r in range(BOARD_SIZE):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Check vertical locations
    for c in range(BOARD_SIZE):
        for r in range(BOARD_SIZE - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Check positively sloped diagonals
    for c in range(BOARD_SIZE - 3):
        for r in range(BOARD_SIZE - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Check negatively sloped diagonals
    for c in range(BOARD_SIZE - 3):
        for r in range(3, BOARD_SIZE):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

    return False

def is_draw(board):
    """Checks if the game is a draw."""
    return np.all(board != EMPTY)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['player1'] = request.form['player1']
        session['player2'] = request.form['player2']
        session['board'] = create_board().tolist()
        session['turn'] = RED
        return redirect(url_for('game'))
    return render_template('index.html')

@app.route('/game')
def game():
    if 'board' not in session:
        return redirect(url_for('index'))
    return render_template('game.html', board=session['board'], player1=session['player1'], player2=session['player2'], turn=session['turn'])

@app.route('/move/<int:col>')
def move(col):
    if 'board' not in session:
        return redirect(url_for('index'))

    board = np.array(session['board'])
    turn = session['turn']

    if is_valid_location(board, col):
        row = get_next_open_row(board, col)
        drop_piece(board, row, col, turn)
        session['board'] = board.tolist()

        if winning_move(board, turn):
            winner = session['player1'] if turn == RED else session['player2']
            return render_template('game.html', board=session['board'], winner=winner, player1=session['player1'], player2=session['player2'])

        if is_draw(board):
            return render_template('game.html', board=session['board'], draw=True, player1=session['player1'], player2=session['player2'])

        session['turn'] = BLUE if turn == RED else RED

    return redirect(url_for('game'))

@app.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)