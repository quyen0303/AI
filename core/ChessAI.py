import random  # Thư viện để chọn nước đi ngẫu nhiên khi cần.

# Biến toàn cục để lưu nước đi tốt nhất tìm được từ thuật toán.
nextMove = None


# Lớp chứa logic AI.
class ChessAI():
    # Hàm khởi tạo, thiết lập các bảng điểm và độ sâu tìm kiếm.
    def __init__(self, depth):
        # TỐI ƯU HÓA: Điểm số quân cờ được nhân với 100 để làm việc với số nguyên, tránh lỗi làm tròn của số thực.
        self.pieceScore = {"K": 0, "Q": 900, "R": 500, "B": 330, "P": 100}

        # Bảng điểm vị trí cho Mã (Knight). Mã ở trung tâm mạnh hơn ở biên.
        self.knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                             [1, 2, 2, 2, 2, 2, 2, 1],
                             [1, 2, 3, 3, 3, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 3, 3, 3, 2, 1],
                             [1, 2, 2, 2, 2, 2, 2, 1],
                             [1, 1, 1, 1, 1, 1, 1, 1]]

        # Bảng điểm vị trí cho Tượng (Bishop). Tượng mạnh hơn trên các đường chéo dài.
        self.bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                             [3, 4, 3, 2, 2, 3, 4, 3],
                             [2, 3, 4, 3, 3, 4, 3, 2],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [1, 2, 3, 4, 4, 3, 2, 1],
                             [2, 3, 4, 3, 3, 4, 3, 1],
                             [3, 4, 3, 2, 2, 3, 4, 3],
                             [4, 3, 2, 1, 1, 1, 3, 4]]

        # Bảng điểm vị trí cho Hậu (Queen).
        self.queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
                            [1, 2, 3, 3, 3, 1, 1, 1],
                            [1, 4, 3, 3, 3, 4, 2, 1],
                            [1, 2, 3, 3, 3, 2, 2, 1],
                            [1, 2, 3, 3, 3, 2, 2, 1],
                            [1, 4, 3, 3, 3, 4, 2, 1],
                            [1, 1, 2, 3, 3, 1, 1, 1],
                            [1, 1, 1, 3, 1, 1, 1, 1]]

        # Bảng điểm vị trí cho Xe (Rook). Xe mạnh trên các hàng và cột mở.
        self.rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
                           [4, 4, 4, 4, 4, 4, 4, 4],
                           [1, 1, 2, 3, 3, 2, 1, 1],
                           [1, 2, 3, 4, 4, 3, 2, 1],
                           [1, 2, 3, 4, 4, 3, 2, 1],
                           [1, 1, 2, 3, 3, 2, 1, 1],
                           [4, 4, 4, 4, 4, 4, 4, 4],
                           [4, 3, 4, 4, 4, 4, 3, 4]]

        # Bảng điểm vị trí cho Tốt trắng (White Pawn). Khuyến khích tốt tiến lên.
        self.whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],  # Hàng cuối để phong cấp.
                                [8, 8, 8, 8, 8, 8, 8, 8],
                                [5, 6, 6, 7, 7, 6, 6, 5],
                                [2, 3, 3, 5, 5, 3, 3, 2],
                                [1, 2, 4, 4, 4, 3, 2, 1],
                                [1, 1, 3, 2, 2, 2, 1, 1],
                                [1, 1, 1, 0, 0, 1, 1, 1],
                                [0, 0, 0, 0, 0, 0, 0, 0]]

        # Bảng điểm vị trí cho Tốt đen (Black Pawn). Tương tự tốt trắng nhưng lật ngược.
        self.blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                                [1, 1, 1, 0, 0, 1, 1, 1],
                                [1, 1, 2, 2, 2, 2, 1, 1],
                                [1, 2, 4, 4, 4, 3, 2, 1],
                                [2, 3, 3, 5, 5, 3, 3, 2],
                                [5, 6, 6, 7, 7, 6, 6, 5],
                                [8, 8, 8, 8, 8, 8, 8, 8],
                                [8, 8, 8, 8, 8, 8, 8, 8]]

        # Bảng điểm vị trí cho Vua (King). Khuyến khích vua an toàn ở giai đoạn đầu và tích cực ở cuối ván cờ.
        self.kingScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [2, 3, 1, 0, 0, 1, 3, 2]]

        # Từ điển gộp tất cả các bảng điểm vị trí.
        self.piecePositionScores = {"N": self.knightScores, "B": self.bishopScores, "Q": self.queenScores,
                                    "R": self.rookScores, "wP": self.whitePawnScores, "bP": self.blackPawnScores,
                                    "K": self.kingScores}

        self.CHECKMATE = 10000  # Điểm cho trạng thái chiếu hết (rất lớn).
        self.STALEMATE = 0  # Điểm cho trạng thái hòa cờ.
        self.DEPTH = depth  # Độ sâu tìm kiếm của thuật toán.

    # Tìm một nước đi ngẫu nhiên từ danh sách các nước đi hợp lệ.
    def findRandomMove(self, validMoves):
        return validMoves[random.randint(0, len(validMoves) - 1)]

    # Hàm chính để tìm nước đi tốt nhất, sử dụng NegaMax với cắt tỉa Alpha-Beta.
    def findBestMoveMinMax(self, gs, validMoves):
        global nextMove
        nextMove = None  # Reset lại nước đi tốt nhất.
        random.shuffle(validMoves)  # Xáo trộn các nước đi để tạo sự đa dạng.
        # Bắt đầu thuật toán tìm kiếm.
        self.findMoveNegaMaxAlphaBeta(gs, validMoves, self.DEPTH, -self.CHECKMATE, self.CHECKMATE,
                                      1 if gs.whiteMoves else -1)
        return nextMove

    # Thuật toán NegaMax với cắt tỉa Alpha-Beta (đệ quy).
    def findMoveNegaMaxAlphaBeta(self, gs, validMoves, depth, alpha, beta, turnMultiplier):
        global nextMove
        # Điều kiện dừng đệ quy: đạt đến độ sâu tìm kiếm tối đa.
        if depth == 0:
            return turnMultiplier * self.scoreBoard(gs)

        # TỐI ƯU HÓA: Sắp xếp nước đi (Move Ordering). Ưu tiên các nước ăn quân.
        orderedMoves = sorted(validMoves, key=lambda move: move.isCapture, reverse=True)

        maxScore = -self.CHECKMATE  # Giả sử điểm số tệ nhất.
        for move in orderedMoves:
            gs.makeMove(move)  # Thử đi.
            nextMoves = gs.getValidMoves()  # Lấy các nước đi tiếp theo.
            # Gọi đệ quy cho lượt của đối thủ.
            score = -self.findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
            if score > maxScore:
                maxScore = score
                if depth == self.DEPTH:  # Nếu ở gốc của cây tìm kiếm, cập nhật nước đi tốt nhất.
                    nextMove = move
            gs.undoMove()  # Hoàn tác nước đi thử.
            # Cắt tỉa Alpha-Beta.
            if maxScore > alpha:  # Cập nhật alpha.
                alpha = maxScore
            if alpha >= beta:  # Nếu alpha >= beta, cắt tỉa nhánh này.
                break
        return maxScore

    # Hàm đánh giá điểm số của bàn cờ hiện tại.
    def scoreBoard(self, gs):
        # Nếu chiếu hết, trả về điểm số tương ứng.
        if gs.checkMate:
            return -self.CHECKMATE if gs.whiteMoves else self.CHECKMATE
        # Nếu hòa cờ, trả về 0.
        elif gs.staleMate:
            return self.STALEMATE

        score = 0
        # Duyệt qua bàn cờ.
        for row in range(len(gs.board)):
            for col in range(len(gs.board[row])):
                square = gs.board[row][col]
                if square != "--":
                    piecePositionScore = 0
                    # Lấy điểm vị trí cho quân Tốt.
                    if square[1] == "P":
                        piecePositionScore = self.piecePositionScores[square[0] + "P"][row][col]
                    # Lấy điểm vị trí cho quân Vua.
                    elif square[1] == "K":
                        piecePositionScore = self.piecePositionScores["K"][row][col]
                    # Lấy điểm vị trí cho các quân khác.
                    else:
                        piecePositionScore = self.piecePositionScores[square[1]][row][col]

                    # Cộng/trừ điểm vào tổng điểm của bàn cờ.
                    if square[0] == 'w':
                        score += self.pieceScore[square[1]] + piecePositionScore
                    elif square[0] == 'b':
                        score -= self.pieceScore[square[1]] + piecePositionScore
        return score

    # Chơi một nước đi từ file PGN.
    def playPGNMove(self, validMoves, i, first_game):
        # Bảng chuyển đổi tọa độ.
        ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                       "5": 3, "6": 2, "7": 1, "8": 0}
        filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                       "e": 4, "f": 5, "g": 6, "h": 7}
        k = 0
        # Duyệt qua các nước đi trong file PGN.
        for move in first_game.mainline_moves():
            k += 1
            if k == i:  # Tìm đến nước đi thứ i.
                moveStr = str(move)  # Chuyển nước đi thành chuỗi (vd: 'e2e4').
                # Tìm nước đi tương ứng trong danh sách các nước đi hợp lệ.
                for playerMove in validMoves:
                    if playerMove.startRow == ranksToRows[moveStr[1]] and \
                            playerMove.startCol == filesToCols[moveStr[0]] and \
                            playerMove.endRow == ranksToRows[moveStr[3]] and \
                            playerMove.endCol == filesToCols[moveStr[2]]:
                        return playerMove  # Trả về nước đi hợp lệ.
        return None