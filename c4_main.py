import chess
import c4_algorithm as al
import re

opening_book = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": "e4",
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1": "c5",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2": "Nf3",
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "d6"
}

def human_move():
    try:
        print(board.legal_moves)
        play = input("Your move: ")
        if (play == "undo"):
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

    color=None

    while(color != "b" and color != "w"):
        color = input("Play as (type 'b' or 'w'): ")

    depth = 0

    while depth == 0:
        depth = int(input("Choose depth: "))

    if color=="b":

        while board.is_checkmate() == False:
            print("The engine is thinking...")
            get_ai_move(depth, chess.WHITE)
            human_move()

    elif color=="w":
        while board.is_checkmate() == False:
            human_move()
            print("The engine is thinking...")
            get_ai_move(depth, chess.BLACK)
    board.reset

board = chess.Board()
startGame()
