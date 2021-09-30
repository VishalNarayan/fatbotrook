import chess
import math
import random


class FatBotEngine:
    def __init__(self, depth=3):
        self.depth = depth
    '''
    METRICS: 
        - material
        - opp choices: # of moves opponent has left
    '''	
    def evalMaterial(self, board): 
        '''
        Given a board position, calculate numeric value of material
        White is + and Black is -
        A score of 0 means that both sides have equal material
        '''
        score = 0
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 100
        }
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if (piece):
                if piece.color:
                    # add
                    score += values[piece.piece_type]
                else:
                    # subtract
                    score -= values[piece.piece_type]

        return score

    def evalOppChoices(self, board):
        num_opp_moves = len(list(board.legal_moves))
        if num_opp_moves == 0:
            score = math.inf
        else:
            score = 1 / num_opp_moves
        if board.turn: # white
            return -score
        else: # black
            return score

    def evalMaster(self, board):
        oppChoicesScore = self.evalOppChoices(board)
        materialScore = self.evalMaterial(board)

        print('oppChoices', oppChoicesScore, 'material', materialScore)
        return 5*oppChoicesScore + materialScore


    def minimax(self, depth, limit, alpha, beta, board):
        if depth == limit:
            return self.evalMaster(board)

        if board.turn: # if white player (maximizer)
            maxEval = -math.inf
            children = list(board.legal_moves)
            for child in children: 
                board.push(child)
                eva = self.minimax(depth+1, limit, alpha, beta, board)
                board.pop()
                maxEval = max(maxEval, eva) # here, if eva is higher, then we also wanna record the depth
                alpha = max(alpha, eva)
                if beta <= alpha:
                    break
            return maxEval
        else: # if black player (minimizer)
            minEval = math.inf
            children = list(board.legal_moves)
            for child in children:
                board.push(child)
                eva = self.minimax(depth+1, limit, alpha, beta, board)
                board.pop()
                minEval = min(minEval, eva)
                beta = min(beta, eva)
                if beta <= alpha:
                    break
            return minEval


    def minimaxRoot(self, depth, limit, alpha, beta, board):
        moves = list(board.legal_moves)

        bestScore = (-1)**(board.turn) * math.inf
        bestMove = None

        if board.turn: # if white player
            for move in moves: 
                board.push(move)
                val = self.minimax(depth+1, limit, alpha, beta, board)
                board.pop()
                print('val', val)
                if val > bestScore:

                    bestScore = val
                    bestMove = move
                    print('changing best move', move, 'score', bestScore)
        else: 
            for move in moves: 
                board.push(move)
                val = self.minimax(depth+1, limit, alpha, beta, board)
                board.pop()
                if val < bestScore:
                    bestScore = val
                    bestMove = move
                    print('changing best move', move, 'score', bestScore)

        if bestMove is None: # if there's only one move left, play it
            print(f"I have {len(moves)} moves left")
            bestMove = moves[0]

        return bestMove


    def search(self, board):
        return self.minimaxRoot(0, self.depth, -math.inf, math.inf, board)
