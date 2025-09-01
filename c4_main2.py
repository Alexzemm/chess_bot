import chess
import c4_algorithm2 as al
import json

with open("opening_book.json", "r") as f:
    opening_book = json.load(f)

def human_move():
    try:
        print(board.legal_moves)
        play = input("Your move: ")
        if play == "undo":
            board.pop()
            board.pop()
            human_move()
            return
        board.push_san(play)
    except:
        human_move()

def get_ai_move(depth, color):
    fen = board.fen()
    if fen in opening_book:
        move = opening_book[fen]
        print(f"Book move: {move}")
        board.push_san(move)
        return

    engine = al.ai(board, depth, color)
    board.push_san(engine.ai_move(board, depth))

def startGame():
    color = None
    while color not in ["b", "w"]:
        color = input("Play as (type 'b' or 'w'): ")

    depth = 0
    while depth == 0:
        depth = int(input("Choose depth: "))

    if color == "b":
        while not board.is_checkmate():
            print("The engine is thinking...")
            get_ai_move(depth, chess.WHITE)
            human_move()

    elif color == "w":
        while not board.is_checkmate():
            human_move()
            print("The engine is thinking...")
            get_ai_move(depth, chess.BLACK)
    board.reset()

board = chess.Board()
startGame()
