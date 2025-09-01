import chess

class ai:

    def __init__(self, board, maxDepth, color):
        self.board = board
        self.color = color
        self.max_quiescence_depth = 3
        # Add transposition table and killer moves
        self.transposition_table = {}
        self.killer_moves = [[None, None] for _ in range(maxDepth + 5)]  # 2 killer moves per depth
        self.history_table = {}  # For history heuristic

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

    def order_moves(self, board, depth=0, hash_move=None):
        def score_move(move):
            score = 0
            
            # Hash move gets highest priority
            if hash_move and move == hash_move:
                return 10000
            
            # Captures (MVV-LVA)
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                score += (victim.piece_type * 10 - attacker.piece_type) if victim and attacker else 0
                score += 1000  # Base capture bonus
            
            # Killer moves
            elif move in self.killer_moves[depth]:
                score += 900
            
            # History heuristic for quiet moves
            else:
                move_key = (move.from_square, move.to_square)
                score += self.history_table.get(move_key, 0)
            
            # Promotion bonus
            if move.promotion:
                score += 800
                
            return score

        moves = list(board.legal_moves)
        moves.sort(key=score_move, reverse=True)
        return moves

    def quiescence(self, board, alpha, beta, depth=0):

        board_hash = hash(board.fen())
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']
        
        stand_pat = self.evaluation(board)
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        if depth >= self.max_quiescence_depth:
            return stand_pat

        for move in self.order_moves(board, depth):
            if board.is_capture(move):
                board.push(move)
                score = self.quiescence(board, alpha, beta, depth + 1)
                board.pop()

                if score >= beta:
                    return beta
                if score > alpha:
                    alpha = score

        self.transposition_table[board_hash] = {'score': alpha, 'depth': depth}
        return alpha

    def minimax(self, board, depth, alpha, beta, maximizing_player):

        board_hash = hash(board.fen())
        hash_move = None
        if board_hash in self.transposition_table:
            entry = self.transposition_table[board_hash]
            if entry['depth'] >= depth:
                return entry['score']
            hash_move = entry.get('best_move')
        
        if depth == 0:
            return self.quiescence(board, alpha, beta)
        if board.is_game_over():
            return self.evaluation(board)

        best_move = None
        original_alpha = alpha

        if maximizing_player:
            max_eval = float('-inf')
            for move in self.order_moves(board, depth, hash_move):
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                    
                alpha = max(alpha, eval)
                if beta <= alpha:

                    if not board.is_capture(move):
                        self.store_killer_move(move, depth)
                        self.update_history(move, depth)
                    break
                    

            if max_eval > original_alpha:
                self.transposition_table[board_hash] = {
                    'score': max_eval, 
                    'depth': depth, 
                    'best_move': best_move
                }
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.order_moves(board, depth, hash_move):
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                    
                beta = min(beta, eval)
                if beta <= alpha:
                    # Store killer move and update history
                    if not board.is_capture(move):
                        self.store_killer_move(move, depth)
                        self.update_history(move, depth)
                    break
                    
            # Store in transposition table
            self.transposition_table[board_hash] = {
                'score': min_eval, 
                'depth': depth, 
                'best_move': best_move
            }
            return min_eval

    def store_killer_move(self, move, depth):

        if depth < len(self.killer_moves):
            if self.killer_moves[depth][0] != move:
                self.killer_moves[depth][1] = self.killer_moves[depth][0]
                self.killer_moves[depth][0] = move

    def update_history(self, move, depth):

        move_key = (move.from_square, move.to_square)
        if move_key not in self.history_table:
            self.history_table[move_key] = 0
        self.history_table[move_key] += depth * depth

    def ai_move(self, board, depth):
        # Clear killer moves for new search
        self.killer_moves = [[None, None] for _ in range(depth + 5)]
        
        best_move = None
        best_eval = float('-inf')
        for move in self.order_moves(board, depth):
            board.push(move)
            eval = self.minimax(board, depth - 1, float('-inf'), float('inf'), False)
            board.pop()
            if eval > best_eval:
                best_eval = eval
                best_move = move

        print(f"AI plays: {best_move} (eval: {best_eval})")
        return board.san(best_move)