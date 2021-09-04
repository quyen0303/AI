import random

class ChessAI():
    __instance = None

    def __new__(cls, depth):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        cls.__instance.depth = depth
        return cls.__instance

    def __call__(cls, *args, **kwargs):
        print(f"The current AI has a depth of {cls.__instance.depth}")

    def __init__(self, depth):
        self.pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 4, "N": 3, "P": 1}
        self.knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                             [1, 2, 2, 2, 2, 2, 2, 1],
                             [1, 2, 3, 3, 3, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 3, 3, 3, 2, 1],
                             [1, 2, 2, 2, 2, 2, 2, 1],
                             [1, 1, 1, 1, 1, 1, 1, 1]]

        self.bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                             [3, 4, 3, 2, 2, 3, 4, 3],
                             [2, 3, 4, 3, 3, 4, 3, 2],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [2, 3, 4, 3, 3, 4, 3, 1],
                             [3, 4, 3, 2, 2, 3, 4, 3],
                             [4, 3, 2, 1, 1, 1, 3, 4]]

        self.queenScores =  [[1, 1, 1, 1, 1, 1, 1, 1],
                             [1, 2, 3, 3, 3, 1, 1, 1],
                             [1, 4, 3, 3, 3, 4, 2, 1],
                             [1, 2, 3, 3, 3, 2, 2, 1],
                             [1, 2, 3, 3, 3, 2, 2, 1],
                             [1, 4, 3, 3, 3, 4, 2, 1],
                             [1, 1, 2, 3, 3, 1, 1, 1],
                             [1, 1, 1, 3, 1, 1, 1, 1]]

        self.rookScores =  [[4, 3, 4, 4, 4, 4, 3, 4],
                            [4, 4, 4, 4, 4, 4, 4, 4],
                            [1, 1, 2, 3, 3, 2, 1, 1],
                            [1, 2, 3, 4, 4, 3, 2, 1],
                            [1, 2, 3, 4, 4, 3, 2, 1],
                            [1, 1, 2, 3, 3, 2, 1, 1],
                            [4, 4, 4, 4, 4, 4, 4, 4],
                            [4, 3, 4, 4, 4, 4, 3, 4]]

        self.whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                                [8, 8, 8, 8, 8, 8, 8, 8],
                                [5, 6, 6, 7, 7, 6, 6, 5],
                                [2, 3, 3, 5, 5, 3, 3, 2],
                                [1, 2, 4, 4, 4, 3, 2, 1],
                                [1, 1, 3, 2, 2, 2, 1, 1],
                                [1, 1, 1, 0, 0, 1, 1, 1],
                                [0, 0, 0, 0, 0, 0, 0, 0]]

        self.blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                                [1, 1, 1, 0, 0, 1, 1, 1],   
                                [1, 1, 2, 2, 2, 2, 1, 1],
                                [1, 2, 4, 4, 4, 3, 2, 1],
                                [2, 3, 3, 5, 5, 3, 3, 2],
                                [5, 6, 6, 7, 7, 6, 6, 5],
                                [8, 8, 8, 8, 8, 8, 8, 8],
                                [8, 8, 8, 8, 8, 8, 8, 8]]

        self.blackKingScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 2, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1]]

        self.whiteKingScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1],
                                [1, 1, 1, 1, 1, 1, 1, 1]]

        self.piecePositionScores = {"N":  self.knightScores,
                                    "B":  self.bishopScores,
                                    "Q":  self.queenScores,
                                    "R":  self.rookScores,
                                    "wP": self.whitePawnScores,
                                    "bP": self.blackPawnScores,
                                    "wK": self.whiteKingScores,
                                    "bK": self.blackKingScores
                                    }
        self.CHECKMATE = 1000
        self.STALEMATE = 0
        self.DEPTH = depth

    def findRandomMove(self, validMoves):
        return validMoves[random.randint(0, len(validMoves)-1)]

    def playPGNMove(self, validMoves, i, first_game):
        ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                       "5": 3, "6": 2, "7": 1, "8": 0}

        filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                       "e": 4, "f": 5, "g": 6, "h": 7}

        board = first_game.board()
        k = 0
        for move in first_game.mainline_moves():
            board.push(move)
            moveStr = str(move)
            k = k + 1
            if k == i:
                for playerMove in validMoves:
                    if playerMove.startRow == ranksToRows[moveStr[1]] and playerMove.startCol == filesToCols[moveStr[0]]\
                            and playerMove.endRow == ranksToRows[moveStr[3]] and playerMove.endCol == filesToCols[moveStr[2]] :
                        return playerMove

    def findBestMove(self, gs, validMoves):

        turnMultiplier = 1 if gs.whiteMoves else -1
        opponentMinMaxScore = self.CHECKMATE
        bestMove = None
        random.shuffle(validMoves)  # pentru varietate
        for playerMove in validMoves:
            gs.makeMove(playerMove)
            opponentMoves = gs.getValidMoves()
            opponentMaxScore = -self.CHECKMATE
            for opponentMove in opponentMoves:
                gs.makeMove(opponentMove)
                if gs.checkMate:
                    score = -turnMultiplier * self.CHECKMATE
                elif gs.staleMate:
                    score = self.STALEMATE
                score = -turnMultiplier * self.scoreMaterial(gs)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
            if opponentMinMaxScore > opponentMaxScore:
                opponentMinMaxScore = opponentMaxScore
                bestMove = playerMove
            gs.undoMove()
        return bestMove

    def findBestMoveMinMax(self, gs, validMoves):
        global nextMove, counter
        counter = 0
        nextMove = None
        random.shuffle(validMoves)
        # findMoveMinMax(gs, DEPTH, gs.whiteMoves)
        # findMoveNegaMax(gs, DEPTH, 1 if gs.whiteMoves else -1)
        self.findMoveNegaMaxAlphaBeta(gs, validMoves, self.DEPTH, -self.CHECKMATE, self.CHECKMATE, 1 if gs.whiteMoves else -1)
        print("Pruned :", counter)
        return nextMove

    def findMoveMinMax(self, gs, validMoves, depth, whiteMoves):
        global nextMove

        if depth == 0:
            return self.scoreMaterial(gs)

        if whiteMoves:
            maxScore = -self.CHECKMATE
            for move in validMoves:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                score = self.findMoveMinMax(gs, nextMoves, depth-1, False)
                if score > maxScore:
                    maxScore = score
                    # nu se mai cauta in adancime
                    if depth == self.DEPTH:
                        nextMove = move
                gs.undoMove()
            return maxScore

        else:
            minScore = self.CHECKMATE
            for move in validMoves:
                gs.makeMove(move)
                nextMoves = gs.getValidMoves()
                score = self.findMoveMinMax(gs, nextMoves, depth - 1, True)
                if score < minScore:
                    minScore = score
                    # nu se mai cauta in adancime
                    if depth == self.DEPTH:
                        nextMove = move
                gs.undoMove()
            return minScore

    def findMoveNegaMax(self, gs, validMoves, depth, turnMultiplier):
        global nextMove, counter
        counter += 1
        if depth == 0:
            return turnMultiplier * self.scoreMaterial(gs)

        maxScore = -self.CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -self.findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
            if score > maxScore:
                maxScore = score
                if depth == self.DEPTH:
                    nextMove = move
            gs.undoMove()

        return maxScore

    def findMoveNegaMaxAlphaBeta(self, gs, validMoves, depth, alpha, beta, turnMultiplier):
        global nextMove, counter
        counter += 1
        if depth == 0:
            return turnMultiplier * self.scoreMaterial(gs)

        maxScore = -self.CHECKMATE

        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -self.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
            if score > maxScore:
                maxScore = score
                if depth == self.DEPTH:
                    nextMove = move
            gs.undoMove()
            if maxScore > alpha:
                alpha = maxScore
            if alpha >= beta:
                break
        return maxScore

    def scoreMaterial(self, gs):

        if gs.checkMate:
            if gs.whiteMoves:
                return -self.CHECKMATE
            else:
                return self.CHECKMATE
        elif gs.staleMate:
            return self.STALEMATE

        score = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    piecePositionScore = 0
                    if square[1] == "P" or square[1] == "K":
                        piecePositionScore = self.piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = self.piecePositionScores[square[1]][row][col]

                    if square[0] == 'w':
                            score += self.pieceScore[square[1]] + piecePositionScore * .1
                    elif square[0] == 'b':
                            score -= self.pieceScore[square[1]] + piecePositionScore * .1

        if gs.whiteCastled:
            score += 1
        else:
            score -= 1

        if gs.blackCastled:
            score -= 1
        else:
            score += 1

        return score
