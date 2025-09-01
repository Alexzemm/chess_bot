import chess

class ai:

    def __init__(self, board, maxDepth, color):
        self.board = board
        self.color = color
        self.max_quiescence_depth = 3


    pst = {
        chess.PAWN: [
            0, 0, 0, 0, 0, 0, 0, 0,
            5, 10, 10, -20, -20, 10, 10, 5,
            5, -5, -10, 0, 0, -10, -5, 5,
            0, 0, 0, 20, 20, 0, 0, 0,
            5, 5, 10, 25, 25, 10, 5, 5,
            10, 10, 20, 30, 30, 20, 10, 10,
            50, 50, 50, 50, 50, 50, 50, 50,
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        chess.KNIGHT: [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20, 0, 0, 0, 0, -20, -40,
            -30, 0, 10, 15, 15, 10, 0, -30,
            -30, 5, 15, 20, 20, 15, 5, -30,
            -30, 0, 15, 20, 20, 15, 0, -30,
            -30, 5, 10, 15, 15, 10, 5, -30,
            -40, -20, 0, 5, 5, 0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50
        ],
        chess.BISHOP: [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 10, 10, 5, 0, -10,
            -10, 5, 5, 10, 10, 5, 5, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10, 5, 0, 0, 0, 0, 5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20
        ],
        chess.ROOK: [
            0, 0, 0, 5, 5, 0, 0, 0,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            -5, 0, 0, 0, 0, 0, 0, -5,
            5, 10, 10, 10, 10, 10, 10, 5,
            0, 0, 0, 0, 0, 0, 0, 0
        ],
        chess.QUEEN: [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 5, 5, 5, 5, 0, -10,
            -5, 0, 5, 5, 5, 5, 0, -5,
            0, 0, 5, 5, 5, 5, 0, -5,
            -10, 5, 5, 5, 5, 5, 0, -10,
            -10, 0, 5, 0, 0, 0, 0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ],
        chess.KING: [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20, 0, 0, 0, 0, 20, 20,
            20, 30, 10, 0, 0, 10, 30, 20
        ]
    }

    def evaluation(self, board):
        if board.is_checkmate():
            return 9999 if board.turn != self.color else -9999
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_threefold_repetition():
            return 0

        score = 0
        piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 1000,
            chess.KING: 20000
        }

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                pst_bonus = self.pst[piece.piece_type][square if piece.color == chess.WHITE else chess.square_mirror(square)]
                scaled_value = value + 0.3 * pst_bonus
                score += scaled_value if piece.color == self.color else -scaled_value

        mobility = len(list(board.legal_moves))
        score += 5 * mobility if board.turn == self.color else -5 * mobility

        if board.is_check():
            score += 50 if board.turn != self.color else -50

        return score


    def order_moves(self, board):
        def score_move(move):
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                return (victim.piece_type * 10 - attacker.piece_type) if victim and attacker else 0
            return 0 

        moves = list(board.legal_moves)
        moves.sort(key=score_move, reverse=True)
        return moves


    def quiescence(self, board, alpha, beta, depth=0):
        stand_pat = self.evaluation(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        if depth >= self.max_quiescence_depth:
            return stand_pat

        for move in self.order_moves(board):
            if board.is_capture(move):
                board.push(move)
                score = self.quiescence(board, alpha, beta, depth + 1)
                board.pop()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        return alpha

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return self.quiescence(board, alpha, beta)
        if board.is_game_over():
            return self.evaluation(board)

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.order_moves(board):
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(eval, max_eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.order_moves(board):
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(eval, min_eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def ai_move(self, board, depth):
        best_move = None
        best_eval = float('-inf')
        for move in self.order_moves(board):
            board.push(move)
            eval = self.minimax(board, depth - 1, float('-inf'), float('inf'), False)
            board.pop()
            if eval > best_eval:
                best_eval = eval
                best_move = move

        print(f"AI plays: {best_move}")
        return board.san(best_move)
