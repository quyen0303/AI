import random

# Biến toàn cục để lưu nước đi tốt nhất tìm được từ thuật toán đệ quy
nextMove = None


class ChessAI():
    def __init__(self, depth):
        # TỐI ƯU HÓA: Nhân điểm số với 100 để dùng số nguyên, tránh float
        self.pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "N": 320, "P": 100}

        # Piece-Square Tables (PSTs) được giữ nguyên, chúng rất quan trọng cho việc đánh giá vị trí
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

        self.queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
                            [1, 2, 3, 3, 3, 1, 1, 1],
                            [1, 4, 3, 3, 3, 4, 2, 1],
                            [1, 2, 3, 3, 3, 2, 2, 1],
                            [1, 2, 3, 3, 3, 2, 2, 1],
                            [1, 4, 3, 3, 3, 4, 2, 1],
                            [1, 1, 2, 3, 3, 1, 1, 1],
                            [1, 1, 1, 3, 1, 1, 1, 1]]

        self.rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
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

        # Bảng điểm cho vua, có thể tùy chỉnh để khuyến khích vua an toàn hoặc di chuyển trong cờ tàn
        self.kingScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [2, 3, 1, 0, 0, 1, 3, 2]]

        self.piecePositionScores = {"N": self.knightScores, "B": self.bishopScores, "Q": self.queenScores,
                                    "R": self.rookScores, "wP": self.whitePawnScores, "bP": self.blackPawnScores,
                                    "K": self.kingScores}

        self.CHECKMATE = 10000
        self.STALEMATE = 0
        self.DEPTH = depth

    def findRandomMove(self, validMoves):
        return validMoves[random.randint(0, len(validMoves) - 1)]

    def findBestMoveMinMax(self, gs, validMoves):
        global nextMove
        nextMove = None
        random.shuffle(validMoves)
        self.findMoveNegaMaxAlphaBeta(gs, validMoves, self.DEPTH, -self.CHECKMATE, self.CHECKMATE,
                                      1 if gs.whiteMoves else -1)
        return nextMove

    def findMoveNegaMaxAlphaBeta(self, gs, validMoves, depth, alpha, beta, turnMultiplier):
        global nextMove
        if depth == 0:
            return turnMultiplier * self.scoreBoard(gs)

        # TỐI ƯU HÓA: Sắp xếp nước đi (Move Ordering)
        # Duyệt các nước đi ăn quân trước để tăng hiệu quả cắt tỉa alpha-beta
        orderedMoves = sorted(validMoves, key=lambda move: move.isCapture, reverse=True)

        maxScore = -self.CHECKMATE
        for move in orderedMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = -self.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
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

    def scoreBoard(self, gs):
        if gs.checkMate:
            return -self.CHECKMATE if gs.whiteMoves else self.CHECKMATE
        elif gs.staleMate:
            return self.STALEMATE

        score = 0
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    piecePositionScore = 0
                    if square[1] == "P":
                        piecePositionScore = self.piecePositionScores[square[0] + "P"][row][col]
                    elif square[1] == "K":
                        # Cân nhắc thêm bảng điểm riêng cho vua trắng và đen
                        piecePositionScore = self.piecePositionScores["K"][row][col]
                    else:
                        piecePositionScore = self.piecePositionScores[square[1]][row][col]

                    if square[0] == 'w':
                        score += self.pieceScore[square[1]] + piecePositionScore
                    elif square[0] == 'b':
                        score -= self.pieceScore[square[1]] + piecePositionScore
        return score

    def playPGNMove(self, validMoves, i, first_game):
        ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                       "5": 3, "6": 2, "7": 1, "8": 0}
        filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                       "e": 4, "f": 5, "g": 6, "h": 7}
        k = 0
        for move in first_game.mainline_moves():
            k += 1
            if k == i:
                moveStr = str(move)
                for playerMove in validMoves:
                    if playerMove.startRow == ranksToRows[moveStr[1]] and \
                            playerMove.startCol == filesToCols[moveStr[0]] and \
                            playerMove.endRow == ranksToRows[moveStr[3]] and \
                            playerMove.endCol == filesToCols[moveStr[2]]:
                        return playerMove
        return None
