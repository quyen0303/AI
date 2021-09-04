import pygame as p

class GameState():
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteMoves = True
        self.moveHistory = []
        self.moveFunctions = {'P' : self.getPawnMoves, 'R' : self.getRookMoves,
                              'N' : self.getKnightMoves, 'B' : self.getBishopMoves,
                              'Q' : self.getQueenMoves, 'K' : self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsHistory = [CastleRights(self.currentCastlingRight.wks,
                                                 self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs,
                                                 self.currentCastlingRight.bqs)]
        self.whiteCastled = False
        self.blackCastled = False
        self.play = 0

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveHistory.append(move)
        self.whiteMoves = not self.whiteMoves

        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            else:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

            if self.whiteMoves:
                self.blackCastled = True
            else:
                self.whiteCastled = True

        self.enpassantPossibleLog.append(self.enpassantPossible)

        self.updateCastleRights(move)
        self.castleRightsHistory.append(CastleRights(self.currentCastlingRight.wks,
                                                      self.currentCastlingRight.bks,
                                                      self.currentCastlingRight.wqs,
                                                      self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveHistory) != 0:
            move = self.moveHistory.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteMoves = not self.whiteMoves

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.castleRightsHistory.pop()
            newRights = self.castleRightsHistory[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

                if self.whiteMoves:
                    self.whiteCastled = False
                else:
                    self.blackCastled = False

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow  == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow  == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
        elif move.pieceCaptured == 'wR':
            if move.endRow  == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured== 'bR':
            if move.endRow  == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRight = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                       self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        moves =  self.getAllPossibleMoves()

        if self.whiteMoves:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            self.whiteMoves = not self.whiteMoves
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteMoves = not self.whiteMoves
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True

                if self.play == 0:
                    checkmateSound = p.mixer.Sound("images/ChessCheckmateSound.mp3")
                    checkmateSound.play()
                    self.play = 1

            else:
                self.staleMate = True
                if self.play == 0:
                    drawSound = p.mixer.Sound("images/ChessDrawSound.mp3")
                    drawSound.play()
                    self.play = 1
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRight
        return moves

    def inCheck(self):
        if self.whiteMoves:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):
        self.whiteMoves = not self.whiteMoves
        opponentMoves = self.getAllPossibleMoves()
        self.whiteMoves = not self.whiteMoves
        for move in opponentMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if(turn == 'w' and self.whiteMoves) or (turn == 'b' and not self.whiteMoves):
                    piece = self.board[row][col][1]
                    self.moveFunctions[piece](row, col, moves)
        return moves

    def getPawnMoves(self, row, col, moves):
        if self.whiteMoves:
            if self.board[row-1][col] == "--": # avansare pion
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row-2][col] == "--":
                    moves.append(Move((row, col), (row-2, col), self.board))

            if col-1 >= 0: # captura pion stanga
                if self.board[row-1][col-1][0] == 'b': # piesa din stanga sus e neagra
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                if (row-1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col-1), self.board, enpassantPossible = True))

            if col+1 <= 7: # captura pion stanga
                if self.board[row-1][col+1][0] == 'b': # piesa din stanga sus e neagra
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                if (row-1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row-1, col+1), self.board, enpassantPossible=True))
        else:
            if self.board[row+1][col] == "--": # avansare pion
                moves.append(Move((row, col), (row+1, col), self.board))
                if row == 1 and self.board[row+2][col] == "--":
                    moves.append(Move((row, col), (row+2, col), self.board))

            if col-1 >= 0: # captura pion stanga
                if self.board[row+1][col-1][0] == 'w': # piesa din stanga sus e neagra
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                if (row+1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col-1), self.board, enpassantPossible=True))

            if col+1 <= 7: # captura pion stanga
                if self.board[row+1][col+1][0] == 'w': # piesa din stanga sus e neagra
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                if (row+1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row+1, col+1), self.board, enpassantPossible=True))

    def getRookMoves(self, row, col, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # sus, stanga, jos, dreapta
        enemyColor = "b" if self.whiteMoves else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break # break aici pentru a nu sari peste piesele adversarului => se uita dupa alta directie
                    else:
                        break # piesa de aceeasi culoare
                else:
                    break # nu se afla pe tabla

    def getKnightMoves(self, row, col, moves):
        directions = ((-2,-1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteMoves else "b"
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # stanga sus, stanga jos, dreapta sus, dreapta jos
        enemyColor = "b" if self.whiteMoves else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break  # break aici pentru a nu sari peste piesele adversarului => se uita dupa alta directie
                    else:
                        break  # piesa de aceeasi culoare
                else:
                    break  # nu se afla pe tabla

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)

    def getKingMoves(self, row, col, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteMoves else "b"
        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    def getCastleMoves(self, row, col, moves):
        # nu se poate face rocada daca regele este in sah
        if self.squareUnderAttack(row, col):
            return

        if (self.whiteMoves and self.currentCastlingRight.wks) or (not self.whiteMoves and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteMoves and self.currentCastlingRight.wqs) or (not self.whiteMoves and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)


    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--":
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, isCastleMove = True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, isCastleMove = True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # dictionare pentru a mapa relatia (rank - file) (linie coloana)
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassantPossible = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False

        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.isPawnPromotion = True

        self.isEnpassantMove = enpassantPossible
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        self.isCastleMove = isCastleMove

        # hash code pentru o mutare
        self.moveID = self.startRow * 1000 + self.startCol * 1000 + self.endRow * 10 + self.endCol
        self.play = 0

    def getChessNotation(self):

        outString = ""
        if self.isPawnPromotion:
            outString += self.getRankFile(self.endRow, self.endCol) + "Q"

        if self.isCastleMove:
            if self.play == 0:
                castleSound = p.mixer.Sound("images/ChessCastleSound.mp3")
                castleSound.play()
                self.play = 1
            if self.endCol > self.startCol:
                outString += "0-0"
            else:
                outString += "0-0-0"

        if self.isEnpassantMove:
            outString += self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.endRow,
                                                                                                    self.endCol) + " e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "P" and not self.isEnpassantMove:
                outString += self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(
                    self.endRow, self.endCol)
            if self.play == 0:
                captureSound = p.mixer.Sound("images/ChessCaptureSound.mp3")
                captureSound.play()
                self.play = 1
            else:
                if self.pieceMoved[1] != "P":
                    outString += self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "P" and not self.isEnpassantMove:
                outString += self.getRankFile(self.endRow, self.endCol)
            elif not self.isCastleMove and not self.isEnpassantMove:
                outString += self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol)

        return outString

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]

    # doua mutari sunt egale daca au aceeasi pozitie initiala si finala si aceeasi piesa s-a mutat
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
