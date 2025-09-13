# Lớp GameState quản lý trạng thái hiện tại của ván cờ.
class GameState():
    # Hàm khởi tạo, thiết lập trạng thái ban đầu của bàn cờ.
    def __init__(self):
        # Biểu diễn bàn cờ bằng một mảng 2D (danh sách của các danh sách).
        # "b" là quân đen (black), "w" là quân trắng (white).
        # "R"-Xe, "N"-Mã, "B"-Tượng, "Q"-Hậu, "K"-Vua, "P"-Tốt.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # Ô trống
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        # Biến boolean để theo dõi lượt đi, True là lượt của quân Trắng.
        self.whiteMoves = True
        # Danh sách lưu lại tất cả các nước đi đã thực hiện.
        self.moveHistory = []
        # Từ điển ánh xạ ký tự quân cờ tới hàm tính nước đi tương ứng.
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves,
                              'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'Q': self.getQueenMoves, 'K': self.getKingMoves}
        # Lưu vị trí vua Trắng để kiểm tra chiếu.
        self.whiteKingLocation = (7, 4)
        # Lưu vị trí vua Đen để kiểm tra chiếu.
        self.blackKingLocation = (0, 4)
        # Cờ báo hiệu trạng thái chiếu hết.
        self.checkMate = False
        # Cờ báo hiệu trạng thái hòa cờ (pat).
        self.staleMate = False
        # Tuple lưu vị trí có thể thực hiện bắt tốt qua đường (en passant).
        self.enpassantPossible = ()
        # Lịch sử các vị trí có thể bắt tốt qua đường.
        self.enpassantPossibleLog = [self.enpassantPossible]
        # Đối tượng lưu quyền nhập thành hiện tại.
        self.currentCastlingRight = CastleRights(True, True, True, True)
        # Lịch sử các quyền nhập thành.
        self.castleRightsHistory = [CastleRights(self.currentCastlingRight.wks,
                                                 self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs,
                                                 self.currentCastlingRight.bqs)]
        # Cờ kiểm tra xem Trắng đã nhập thành chưa.
        self.whiteCastled = False
        # Cờ kiểm tra xem Đen đã nhập thành chưa.
        self.blackCastled = False

    # Hàm thực hiện một nước đi.
    def makeMove(self, move):
        # Dọn ô cờ bắt đầu.
        self.board[move.startRow][move.startCol] = "--"
        # Di chuyển quân cờ đến ô kết thúc.
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # Thêm nước đi vào lịch sử.
        self.moveHistory.append(move)
        # Đổi lượt đi.
        self.whiteMoves = not self.whiteMoves

        # Cập nhật vị trí vua Trắng nếu vua di chuyển.
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        # Cập nhật vị trí vua Đen nếu vua di chuyển.
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Xử lý phong cấp cho tốt (mặc định thành Hậu).
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Xử lý nước bắt tốt qua đường.
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # Xóa quân tốt bị bắt.

        # Nếu tốt tiến 2 ô, đánh dấu ô phía sau nó là có thể bắt qua đường.
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()  # Reset lại nếu không phải.

        # Xử lý nước đi nhập thành.
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Nhập thành cánh vua.
                # Di chuyển quân Xe.
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # Nhập thành cánh hậu.
                # Di chuyển quân Xe.
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
            # Đánh dấu đã nhập thành.
            if self.whiteMoves:
                self.blackCastled = True
            else:
                self.whiteCastled = True

        # Cập nhật lịch sử bắt tốt qua đường và quyền nhập thành.
        self.enpassantPossibleLog.append(self.enpassantPossible)
        self.updateCastleRights(move)
        self.castleRightsHistory.append(CastleRights(self.currentCastlingRight.wks,
                                                     self.currentCastlingRight.bks,
                                                     self.currentCastlingRight.wqs,
                                                     self.currentCastlingRight.bqs))

    # Hàm hoàn tác nước đi cuối cùng.
    def undoMove(self):
        # Chỉ hoàn tác nếu có nước đi trong lịch sử.
        if len(self.moveHistory) != 0:
            # Lấy nước đi cuối cùng ra khỏi lịch sử.
            move = self.moveHistory.pop()
            # Đặt lại quân cờ đã di chuyển về vị trí cũ.
            self.board[move.startRow][move.startCol] = move.pieceMoved
            # Phục hồi quân cờ đã bị bắt (nếu có).
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # Đổi lại lượt đi.
            self.whiteMoves = not self.whiteMoves

            # Cập nhật lại vị trí vua nếu vua đã di chuyển.
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Hoàn tác nước bắt tốt qua đường.
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # Ô đích trở thành trống.
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # Đặt lại tốt bị bắt.

            # Khôi phục trạng thái bắt tốt qua đường từ lịch sử.
            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            # Khôi phục quyền nhập thành từ lịch sử.
            self.castleRightsHistory.pop()
            newRights = self.castleRightsHistory[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            # Hoàn tác nước nhập thành.
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Nhập thành cánh vua
                    # Di chuyển Xe về vị trí cũ.
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Nhập thành cánh hậu
                    # Di chuyển Xe về vị trí cũ.
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

                # Đặt lại cờ đã nhập thành.
                if self.whiteMoves:
                    self.whiteCastled = False
                else:
                    self.blackCastled = False

            # Reset lại trạng thái kết thúc game.
            self.checkMate = False
            self.staleMate = False

    # Cập nhật quyền nhập thành sau mỗi nước đi.
    def updateCastleRights(self, move):
        # Nếu vua trắng di chuyển, mất cả hai quyền nhập thành.
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        # Tương tự với vua đen.
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        # Nếu xe trắng di chuyển, mất quyền nhập thành ở cánh tương ứng.
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # Xe cánh hậu
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  # Xe cánh vua
                    self.currentCastlingRight.wks = False
        # Tương tự với xe đen.
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # Xe cánh hậu
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  # Xe cánh vua
                    self.currentCastlingRight.bks = False

        # Nếu một quân xe bị bắt, bên đó cũng mất quyền nhập thành ở cánh tương ứng.
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    # Lấy tất cả các nước đi hợp lệ.
    def getValidMoves(self):
        # Lưu trạng thái tạm thời của enpassant và quyền nhập thành.
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRight = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        # 1. Lấy tất cả các nước đi có thể (chưa kiểm tra chiếu).
        moves = self.getAllPossibleMoves()
        # Thêm các nước đi nhập thành.
        if self.whiteMoves:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # 2. Với mỗi nước đi, thực hiện nó và kiểm tra xem vua có bị chiếu không.
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])  # Thử đi nước cờ.
            # Đổi lượt để kiểm tra xem vua của người vừa đi có bị đối phương tấn công không.
            self.whiteMoves = not self.whiteMoves
            if self.inCheck():
                moves.remove(moves[i])  # Nếu vua bị chiếu, nước đi không hợp lệ.
            # Đổi lại lượt.
            self.whiteMoves = not self.whiteMoves
            self.undoMove()  # Hoàn tác nước đi thử.

        # 3. Kiểm tra chiếu hết hoặc hòa cờ.
        if len(moves) == 0:  # Nếu không có nước đi hợp lệ nào.
            if self.inCheck():  # Và đang bị chiếu.
                self.checkMate = True  # -> Chiếu hết.
            else:  # Nếu không bị chiếu.
                self.staleMate = True  # -> Hòa cờ (pat).
        else:
            self.checkMate = False
            self.staleMate = False

        # Khôi phục lại trạng thái enpassant và nhập thành.
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRight
        return moves

    # Kiểm tra xem vua của người chơi hiện tại có đang bị chiếu không.
    def inCheck(self):
        if self.whiteMoves:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    # Kiểm tra xem một ô cờ có đang bị đối phương tấn công không.
    def squareUnderAttack(self, row, col):
        self.whiteMoves = not self.whiteMoves  # Tạm thời đổi sang lượt đối phương.
        opponentMoves = self.getAllPossibleMoves()  # Lấy tất cả nước đi của đối phương.
        self.whiteMoves = not self.whiteMoves  # Đổi lại lượt.
        for move in opponentMoves:
            if move.endRow == row and move.endCol == col:  # Nếu có nước đi tới ô đó.
                return True  # Ô đang bị tấn công.
        return False

    # Lấy tất cả các nước đi có thể, không kiểm tra chiếu.
    def getAllPossibleMoves(self):
        moves = []
        # Duyệt qua từng ô trên bàn cờ.
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]  # Lấy màu quân cờ ('w' hoặc 'b').
                # Nếu là quân cờ của người chơi hiện tại.
                if (turn == 'w' and self.whiteMoves) or (turn == 'b' and not self.whiteMoves):
                    piece = self.board[row][col][1]  # Lấy loại quân cờ ('P', 'R', ...).
                    self.moveFunctions[piece](row, col, moves)  # Gọi hàm tương ứng để lấy nước đi.
        return moves

    # Lấy các nước đi của Tốt.
    def getPawnMoves(self, row, col, moves):
        if self.whiteMoves:  # Tốt trắng
            # Đi thẳng 1 ô
            if self.board[row - 1][col] == "--":
                moves.append(Move((row, col), (row - 1, col), self.board))
                # Đi thẳng 2 ô từ vị trí ban đầu
                if row == 6 and self.board[row - 2][col] == "--":
                    moves.append(Move((row, col), (row - 2, col), self.board))
            # Ăn chéo trái
            if col - 1 >= 0:
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
                elif (row - 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, enpassantPossible=True))
            # Ăn chéo phải
            if col + 1 <= 7:
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
                elif (row - 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, enpassantPossible=True))
        else:  # Tốt đen
            # Đi thẳng 1 ô
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                # Đi thẳng 2 ô từ vị trí ban đầu
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            # Ăn chéo trái
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row + 1, col - 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, enpassantPossible=True))
            # Ăn chéo phải
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row + 1, col + 1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, enpassantPossible=True))

    # Lấy các nước đi của Xe.
    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Lên, trái, xuống, phải
        enemyColor = "b" if self.whiteMoves else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Trong bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Ô trống, có thể đi
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Gặp quân địch, ăn và dừng
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # Gặp quân mình, dừng
                        break
                else:  # Ngoài bàn cờ, dừng
                    break

    # Lấy các nước đi của Mã.
    def getKnightMoves(self, row, col, moves):
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # 8 hướng đi chữ L
        allyColor = "w" if self.whiteMoves else "b"
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Nếu không phải quân mình (trống hoặc quân địch)
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    # Lấy các nước đi của Tượng.
    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 hướng chéo
        enemyColor = "b" if self.whiteMoves else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # Trong bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # Ô trống
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Quân địch
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # Quân mình
                        break
                else:  # Ngoài bàn cờ
                    break

    # Lấy các nước đi của Hậu (kết hợp Xe và Tượng).
    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    # Lấy các nước đi của Vua.
    def getKingMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))  # 8 hướng xung quanh
        allyColor = "w" if self.whiteMoves else "b"
        for i in range(8):
            endRow = row + directions[i][0]
            endCol = col + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Không phải quân mình
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    # Lấy các nước đi nhập thành.
    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):  # Nếu vua đang bị chiếu thì không được nhập thành.
            return
        # Kiểm tra nhập thành cánh vua.
        if (self.whiteMoves and self.currentCastlingRight.wks) or \
                (not self.whiteMoves and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        # Kiểm tra nhập thành cánh hậu.
        if (self.whiteMoves and self.currentCastlingRight.wqs) or \
                (not self.whiteMoves and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    # Lấy nước đi nhập thành cánh vua.
    def getKingsideCastleMoves(self, row, col, moves):
        # Các ô giữa vua và xe phải trống.
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            # Các ô vua đi qua không được bị tấn công.
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCastleMove=True))

    # Lấy nước đi nhập thành cánh hậu.
    def getQueensideCastleMoves(self, row, col, moves):
        # Các ô giữa vua và xe phải trống.
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            # Các ô vua đi qua không được bị tấn công.
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCastleMove=True))


# Lớp lưu trữ quyền nhập thành.
class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # white king side
        self.bks = bks  # black king side
        self.wqs = wqs  # white queen side
        self.bqs = bqs  # black queen side


# Lớp biểu diễn một nước đi.
class Move:
    # Ánh xạ ký hiệu tọa độ cờ vua sang chỉ số mảng.
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible=False, isCastleMove=False):
        self.startRow = startSq[0]  # Hàng bắt đầu
        self.startCol = startSq[1]  # Cột bắt đầu
        self.endRow = endSq[0]  # Hàng kết thúc
        self.endCol = endSq[1]  # Cột kết thúc
        self.pieceMoved = board[self.startRow][self.startCol]  # Quân cờ di chuyển
        self.pieceCaptured = board[self.endRow][self.endCol]  # Quân cờ bị bắt

        # TỐI ƯU HÓA: Cờ để AI dễ dàng sắp xếp các nước đi ăn quân lên trước.
        self.isCapture = self.pieceCaptured != '--'

        # Cờ kiểm tra phong cấp.
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or \
                               (self.pieceMoved == 'bP' and self.endRow == 7)

        # Cờ kiểm tra bắt tốt qua đường.
        self.isEnpassantMove = enpassantPossible
        if self.isEnpassantMove:
            # Xác định quân tốt bị bắt trong trường hợp en passant.
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        # Cờ kiểm tra nhập thành.
        self.isCastleMove = isCastleMove
        # Tạo một ID duy nhất cho mỗi nước đi để so sánh.
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # So sánh hai đối tượng Move.
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    # Chuyển nước đi thành ký hiệu cờ vua tiêu chuẩn (ví dụ: e4, Nf3, 0-0).
    def getChessNotation(self):
        if self.isPawnPromotion:
            return self.getRankFile(self.endRow, self.endCol) + "Q"
        if self.isCastleMove:
            return "0-0" if self.endCol > self.startCol else "0-0-0"
        if self.isEnpassantMove:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + \
                self.getRankFile(self.endRow, self.endCol) + " e.p."

        if self.isCapture:  # Nước đi ăn quân
            if self.pieceMoved[1] == "P":  # Tốt ăn
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + \
                    self.getRankFile(self.endRow, self.endCol)
            else:  # Quân khác ăn
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:  # Nước đi không ăn quân
            if self.pieceMoved[1] == "P":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

    # Lấy ký hiệu tọa độ (ví dụ: "a1") từ chỉ số hàng và cột.
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]