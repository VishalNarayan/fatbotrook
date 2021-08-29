"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""

import chess
import random
import math
from engine_wrapper import EngineWrapper


class FillerEngine:
    """
    Not meant to be an actual engine.

    This is only used to provide the property "self.engine"
    in "MinimalEngine" which extends "EngineWrapper"
    """
    def __init__(self, main_engine, name=None):
        self.id = {
            "name": name
        }
        self.name = name
        self.main_engine = main_engine

    def __getattr__(self, method_name):
        main_engine = self.main_engine

        def method(*args, **kwargs):
            nonlocal main_engine
            nonlocal method_name
            return main_engine.notify(method_name, *args, **kwargs)

        return method


class MinimalEngine(EngineWrapper):
    """
    Subclass this to prevent a few random errors

    Even though MinimalEngine extends EngineWrapper,
    you don't have to actually wrap an engine.

    At minimum, just implement `search`,
    however you can also change other methods like
    `notify`, `first_search`, `get_time_control`, etc.
    """
    def __init__(self, *args, name=None):
        super().__init__(*args)

        self.engine_name = self.__class__.__name__ if name is None else name

        self.last_move_info = []
        self.engine = FillerEngine(self, name=self.name)
        self.engine.id = {
            "name": self.engine_name
        }

    def search_with_ponder(self, board, wtime, btime, winc, binc, ponder):
        timeleft = 0
        if board.turn:
            timeleft = wtime
        else:
            timeleft = btime
        return self.search(board, timeleft, ponder)

    def search(self, board, timeleft, ponder):
        raise NotImplementedError("The search method is not implemented")

    def notify(self, method_name, *args, **kwargs):
        """
        The EngineWrapper class sometimes calls methods on "self.engine".
        "self.engine" is a filler property that notifies <self> 
        whenever an attribute is called.

        Nothing happens unless the main engine does something.

        Simply put, the following code is equivalent
        self.engine.<method_name>(<*args>, <**kwargs>)
        self.notify(<method_name>, <*args>, <**kwargs>)
        """
        pass


class ExampleEngine(MinimalEngine):
    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    def search(self, board, *args):
        print('aquiiiiii')
        return random.choice(list(board.legal_moves))


class Alphabetical(ExampleEngine):
    def search(self, board, *args):
        moves = list(board.legal_moves)
        moves.sort(key=board.san)
        return moves[0]


class FirstMove(ExampleEngine):
    """Gets the first move when sorted by uci representation"""
    def search(self, board, *args):
        moves = list(board.legal_moves)
        moves.sort(key=str)
        return moves[0]



class VishalMove(ExampleEngine):
    def evalMaterial(self, board): # this is a metric
        # given a board position, return a numeric value 
        # for squares 0 to 63
        #   if there's a piece on the square, find the piece
        #   add or subtract to the total score
        # return score
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

    def evalOppChoices(self, board): # this is a metric
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

        #print('oppChoices', oppChoicesScore, 'material', materialScore)
        return oppChoicesScore + materialScore

    def limit_play(self, board, *args):
        moves = list(board.legal_moves)
        random.shuffle(moves)
        best_limit = math.inf
        best_move = None
        checking_moves = {}
        for move in moves:
            num_opp_moves = self.evalOppChoices(board, move)

            if board.gives_check(move):
                checking_moves[move] = num_opp_moves

            if num_opp_moves < best_limit:
                best_limit = num_opp_moves
                best_move = move

        print('found!')

        if len(checking_moves) > 0:
            return min(checking_moves, key=checking_moves.get)
        else:
            return best_move




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

        return bestMove
    def search(self, board, *args):


        # TRY THESE METRICS:

        # minimum # of opponent moves (limit_play)
        #return self.limit_play(board, *args)

        return self.minimaxRoot(0, 3, -math.inf, math.inf, board)


        # MINIMAX EXCEPT DON'T CONSIDER THE OTHER PLAYER'S MOVES
            # TREAT IT LIKE A 1 PLAYER GAME


        '''
        moves = list(board.legal_moves)
        #print(moves)
        best_score = self.evaluate(board)
        best_move = random.choice(moves)

        ideal_moves = []
        check_moves = []
        for move in moves: 

            board.push(move)
            score = self.evaluate(board)
            board.pop()
            if board.turn == chess.WHITE:
                if score > best_score:
                    best_score = score
                    best_move = move
                    ideal_moves = [move]
                elif score == best_score:
                    ideal_moves.append(move)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                    ideal_moves = [move]
                elif score == best_score:
                    ideal_moves.append(move)
        
        print(ideal_moves)
        return random.choice(ideal_moves)
        '''
