import ChessView, ChessEngine, ChessAI, ChessMain, ChessObserver
import pygame as p
import tkinter as tk
from tkinter import filedialog
import chess.pgn

class ChessController():
    def __init__(self):
        self.chessView = ChessView.ChessView()
        self.chessView.loadBoard()
        self.chessModel = ChessEngine.GameState()

    def animateMove(self, move, clock):
        colors = [p.Color(235, 235, 208), p.Color(119, 148, 85)]
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        framesPerSquare = 5
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        for frame in range(frameCount + 1):
            row, col = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
            self.chessView.drawBoard()
            self.chessView.drawPieces(self.chessModel.board)
            color = colors[(move.endRow + move.endCol) % 2]
            endSquare = p.Rect(move.endCol * self.chessView.SQUARE_SIZE, move.endRow * self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE)
            p.draw.rect(self.chessView.screen, color, endSquare)
            if move.pieceCaptured != "--":
                if move.isEnpassantMove:
                    enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == "b" else move.endRow -1
                    endSquare = p.Rect(move.endCol * self.chessView.SQUARE_SIZE, enPassantRow * self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE)
                self.chessView.screen.blit(self.chessView.IMAGES[move.pieceCaptured], endSquare)
            self.chessView.screen.blit(self.chessView.IMAGES[move.pieceMoved], p.Rect(col * self.chessView.SQUARE_SIZE, row * self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE))
            p.display.flip()
            clock.tick(60)

    def highlightSquares(self, selected):
        if selected != ():
            row, col = selected
            if self.chessModel.board[row][col][0] == ("w" if self.chessModel.whiteMoves else "b"):
                s = p.Surface((self.chessView.SQUARE_SIZE, self.chessView.SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(p.Color("blue"))
                self.chessView.screen.blit(s, (col * self.chessView.SQUARE_SIZE, row * self.chessView.SQUARE_SIZE))
                s.fill(p.Color("yellow"))
                for move in self.chessModel.getValidMoves():
                    if move.startRow == row and move.startCol == col:
                        self.chessView.screen.blit(s, (move.endCol * self.chessView.SQUARE_SIZE, move.endRow * self.chessView.SQUARE_SIZE))

    def drawGameState(self, selected, AI, chessPub):
        self.chessView.drawBoard()
        self.highlightSquares(selected)
        self.chessView.drawPieces(self.chessModel.board)
        self.drawMoveLog()
        chessPub.notify(str("{:.2f}".format(AI.scoreMaterial(self.chessModel))), AI, self)

    def checkStringInFile(self, file, string):
        with open(file, 'r') as read_obj:
            for line in read_obj:
                if string in line:
                    return True
        return False

    def drawEvalBar(self, AI):

        if self.chessModel.checkMate != True:
            outString = str("{:.1f}".format(AI.scoreMaterial(self.chessModel)))
            barStart = self.chessView.MOVE_LOG_WIDTH - 10 * AI.scoreMaterial(self.chessModel)
        else:
            if self.chessModel.whiteMoves:
                outString = "0-1"
                barStart = self.chessView.HEIGHT
            else:
                outString = "1-0"
                barStart = 0

        p.draw.rect(self.chessView.screen, p.Color("White"),
                    p.Rect(self.chessView.HEIGHT,
                           barStart, 40,
                           self.chessView.HEIGHT))
        p.draw.rect(self.chessView.screen, p.Color("Black"),
                    p.Rect(self.chessView.HEIGHT,
                           0, 40,
                           barStart))

        if AI.scoreMaterial(self.chessModel) <= -1:
            chatColor = p.Color("White")
        else:
            if AI.scoreMaterial(self.chessModel) <= 1 and AI.scoreMaterial(self.chessModel) >= -1 :
                chatColor = p.Color("Gray")
            else:
                chatColor = p.Color("Black")

        self.chessView.drawMenuText(outString, chatColor, self.chessView.WIDTH + 3, self.chessView.HEIGHT/2)

    def drawMoveLog(self):
        moveLogRect = p.Rect(self.chessView.HEIGHT + 35, 0, self.chessView.MOVE_LOG_WIDTH + self.chessView.EVAL_BAR_WIDTH, self.chessView.HEIGHT)
        p.draw.rect(self.chessView.screen, p.Color("Black"), moveLogRect)
        moveLog = self.chessModel.moveHistory
        moveTexts = []
        for i in range(0, len(moveLog), 2):
            moveString = " " + str(i // 2 + 1) + ")" + moveLog[i].getChessNotation() + " "
            if i + 1 < len(moveLog):
                moveString += moveLog[i+1].getChessNotation()
            moveTexts.append(moveString)
        padding = 5
        movesPerRow = 2
        textY = padding
        for i in range(0, len(moveTexts), movesPerRow):
            text = ""
            for j in range(movesPerRow):
                if i + j < len(moveTexts):
                    text += moveTexts[i+j]
            textObject = self.chessView.font.render(text, True, p.Color("White"))
            textLocation = moveLogRect.move(padding, textY)
            self.chessView.screen.blit(textObject, textLocation)
            textY += textObject.get_height()

    def runGame(self, playerOne, playerTwo, windowText, depth, language, subscribed, importGame):
        p.init()
        selected = ()
        clicked = []
        clock = p.time.Clock()
        animate = False
        AI = ChessAI.ChessAI(depth)
        AI()
        playSound = p.mixer.Sound("images/ChessOpeningSound.mp3")
        playSound.play()
        p.mixer.init()
        gs = self.chessModel
        view = self.chessView
        view.screen = p.display.set_mode((view.WIDTH + view.MOVE_LOG_WIDTH, view.HEIGHT))
        validMoves = gs.getValidMoves()
        moveMade = False
        p.display.set_caption(windowText)
        gameOver = False
        whiteChecked = ""
        blackChecked = ""
        running = True
        movesList = []
        lastMovePrinted = False
        repetitionDraw = False
        resigned = False
        lenMoves = 1
        pgn = []

        if importGame == True:
            root = tk.Tk()
            root.withdraw()
            file = filedialog.askopenfilename()
            try:
                pgn = open(file)
            except FileNotFoundError:
                print("Wrong file or file path")
            first_game = chess.pgn.read_game(pgn)
            for move in first_game.mainline_moves():
                lenMoves = lenMoves + 1

        pgnCount = 1
        chessPub = ChessObserver.ChessPublisher()
        chessSub = ChessObserver.ChessSubscriber("viewer")
        if subscribed == True:
            chessPub.register(chessSub)
        turn = 1
        play = 0
        while running:
            humanTurn = (gs.whiteMoves and playerOne) or (not gs.whiteMoves and playerTwo)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                    p.quit()
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gameOver and humanTurn:
                        location = p.mouse.get_pos()
                        col = location[0] // view.SQUARE_SIZE
                        row = location[1] // view.SQUARE_SIZE
                        if selected == (row, col) or col >= 8:  # se apasa pe acelasi patrat de 2 ori
                            selected = ()
                            clicked = []
                        else:
                            selected = (row, col)
                            clicked.append(selected)
                        if len(clicked) == 2:  # daca lista are 2 elemente atunci se face mutarea
                            move = ChessEngine.Move(clicked[0], clicked[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    moveSound = p.mixer.Sound("images/ChessMoveSound.mp3")
                                    moveSound.play()
                                    animate = True
                                    selected = ()
                                    clicked = []
                            if not moveMade:
                                clicked = [selected]

                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z:
                        if (len(gs.moveHistory) > 0):
                            gs.undoMove()
                            if gs.whiteMoves:
                                if turn > 1:
                                    turn -= 1
                            moveMade = True
                            animate = False
                            gameOver = False
                            lastMovePrinted = False

                    if e.key == p.K_r:
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        selected = ()
                        clicked = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        turn = 1
                        lastMovePrinted = False
                        movesList = []
                        ChessMain.main(language, subscribed)

                    if e.key == p.K_s:
                        gs.checkMate = True
                        resigned = True

                # AI
                if not gameOver and not humanTurn:
                        if importGame == False:
                            if depth <= 2:
                                AIMove = AI.findBestMove(gs, validMoves)
                            else:
                               AIMove = AI.findBestMoveMinMax(gs, validMoves)

                            if AIMove is None:
                                 AIMove = AI.findRandomMove(validMoves)

                            gs.makeMove(AIMove)

                        else:
                            if pgnCount <= lenMoves and importGame == True:
                                AIMove = AI.playPGNMove(validMoves, pgnCount, first_game)
                                pgnCount = pgnCount + 1
                            else:
                                 gameOver = True

                            if pgnCount <= lenMoves and importGame == True:
                                gs.makeMove(AIMove)
                            else:
                                gameOver = True

                        if playerTwo == True or playerOne == True:
                            humanTurn = True

                        p.mixer.init()
                        moveSound = p.mixer.Sound("images/ChessMoveSound.mp3")
                        moveSound.play()

                        moveMade = True

                        if not gameOver:
                            animate = True

                import xml.etree.ElementTree as ET
                mytree = ET.parse("display.xml")
                myroot = mytree.getroot()

                for x in myroot.findall(language):
                    drawText = x.find("draw").text
                    whiteText = x.find("whitewin").text
                    blackText = x.find("blackwin").text
                    stalemateText = x.find("stalemate").text
                    humanResignText = x.find("humanresign").text
                    whiteResignText = x.find("whiteresign").text
                    blackResignText = x.find("blackresign").text
                    agreementText = x.find("agreement").text

                if moveMade:
                    if not gs.whiteMoves and gs.inCheck():
                        whiteChecked = "+"
                    elif gs.whiteMoves and gs.inCheck():
                        blackChecked = "+"

                    #if (len(gs.moveHistory) >= 1):
                        #print("Last move : " + gs.moveHistory[-1].getChessNotation() + "\n")

                    if len(gs.moveHistory) >= 10 and gs.moveHistory[-1].getChessNotation() == gs.moveHistory[
                        -5].getChessNotation() \
                            and gs.moveHistory[-5].getChessNotation() == gs.moveHistory[-9].getChessNotation() and \
                            gs.moveHistory[-2].getChessNotation() == gs.moveHistory[-6].getChessNotation() and \
                            gs.moveHistory[-6].getChessNotation() == gs.moveHistory[-10].getChessNotation() and \
                            gs.moveHistory[-3].getChessNotation() == gs.moveHistory[-7].getChessNotation() and \
                            gs.moveHistory[-4].getChessNotation() == gs.moveHistory[-8].getChessNotation():
                        gameOver = True
                        print("Draw by repetition")
                        view.drawText(drawText)
                        repetitionDraw = True

                    if animate:
                        self.animateMove(gs.moveHistory[-1], clock)

                    validMoves = gs.getValidMoves()
                    moveMade = False
                    animate = False
                    if gs.whiteMoves and len(gs.moveHistory) >= 1:
                        movesList.append(
                            f"\n{turn}. {gs.moveHistory[-2].getChessNotation()}{whiteChecked} "
                            f"{gs.moveHistory[-1].getChessNotation()}{blackChecked}")
                        turn += 1
                        whiteChecked = ""
                        blackChecked = ""

                self.drawGameState(selected, AI, chessPub)

                if gs.checkMate and resigned == False:
                    gameOver = True
                    if gs.whiteMoves:
                        view.drawText(blackText)
                        if not lastMovePrinted:
                            if len(movesList) > 0:
                                newLast = movesList[-1][:-1]
                                movesList[-1] = newLast + "#"
                                movesList.append("result 0-1")
                                lastMovePrinted = True
                                view.saveGame(movesList)
                    else:
                        view.drawText(whiteText)
                        if not lastMovePrinted:
                            movesList.append(f"\n{turn}. {gs.moveHistory[-1].getChessNotation()}#")
                            movesList.append("result: 1-0")
                            lastMovePrinted = True
                            view.saveGame(movesList)

                elif gs.staleMate:
                    gameOver = True
                    view.drawText(stalemateText)
                    if not lastMovePrinted:
                        if not gs.whiteMoves:
                            movesList.append(f"\n{turn}. {gs.moveHistory[-1].getChessNotation()}")
                            movesList.append("result: 1/2-1/2")
                            lastMovePrinted = True
                            view.saveGame(movesList)

                elif repetitionDraw:
                    view.drawText(drawText)
                    if play == 0:
                        drawSound = p.mixer.Sound("images/ChessDrawSound.mp3")
                        drawSound.play()
                        play = 1

                if gs.checkMate and resigned and (playerOne == True or playerTwo == True):
                    gameOver = True
                    view.drawText(humanResignText)
                    if play == 0:
                        drawSound = p.mixer.Sound("images/ChessDrawSound.mp3")
                        drawSound.play()
                        play = 1

                if not gs.checkMate and importGame == True and gameOver == True:

                    if self.checkStringInFile(file, "1/2-1/2"):
                        view.drawText(agreementText)
                    if self.checkStringInFile(file, "1-0"):
                        view.drawText(blackResignText)
                    if self.checkStringInFile(file, "0-1"):
                         view.drawText(whiteResignText)
                    if play == 0:
                        drawSound = p.mixer.Sound("images/ChessDrawSound.mp3")
                        drawSound.play()
                        play = 1
                        
                clock.tick(view.FPS)
                p.display.flip()

    def playGame(self, language, subscribed):
        self.chessView.mainMenu(language, subscribed)
        mx, my = p.mouse.get_pos()
        if self.chessView.buttons["buttonAIvsAI"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(False, False, "AI vs AI", 2, language, subscribed, False)
        if self.chessView.buttons["buttonWhitevsAI"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(True, False, "Human (White) vs AI (Black)", 2, language, subscribed, False)
        if self.chessView.buttons["buttonAIvsBlack"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(False, True, "AI (White) vs Human (Black)", 2, language, subscribed, False)
        if self.chessView.buttons["buttonHumanvsHuman"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(True, True, "Practice Mode", 2, language, subscribed, False)
        if self.chessView.buttons["buttonHardAIvsHardAI"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(False, False, "AI vs AI (Depth 3)", 3, language, subscribed, False)
        if self.chessView.buttons["buttonWhitevsHardAI"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(True, False, "Human (White) vs Strong AI (Depth 3)", 3, language, subscribed, False)
        if self.chessView.buttons["buttonImport"].collidepoint((mx, my)):
            if self.chessView.click:
                self.runGame(False, False, "AI vs AI", 2, language, subscribed, True)
        if self.chessView.buttons["buttonRomanian"].collidepoint((mx, my)):
            ChessMain.main("romanian", subscribed)
        if self.chessView.buttons["buttonEnglish"].collidepoint((mx, my)):
            ChessMain.main("english", subscribed)
        if self.chessView.buttons["buttonGerman"].collidepoint((mx, my)):
            ChessMain.main("german", subscribed)
        if self.chessView.buttons["buttonRussian"].collidepoint((mx, my)):
            ChessMain.main("russian", subscribed)
        if self.chessView.buttons["buttonSubscribe"].collidepoint((mx, my)):
            subscribed = not subscribed
            ChessMain.main(language, subscribed)