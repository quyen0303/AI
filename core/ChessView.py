import os

import pygame as p
import sys
from pygame.locals import *

class ChessView():
    def __init__(self):
        p.init()
        self.WIDTH = self.HEIGHT = self.MOVE_LOG_HEIGHT = 512
        self.MOVE_LOG_WIDTH = 280
        self.EVAL_BAR_WIDTH = 50
        self.n = 8
        self.SQUARE_SIZE = self.HEIGHT // self.n
        self.FPS = 15
        self.IMAGES = {}
        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.click = False
        self.buttons = {"buttonAIvsAI": p.Rect(56, 120, 400, 56),
                        "buttonWhitevsAI": p.Rect(56, 180, 400, 56),
                        "buttonAIvsBlack": p.Rect(56, 240, 400, 56),
                        "buttonHumanvsHuman": p.Rect(56, 300, 400, 56),
                        "buttonHardAIvsHardAI": p.Rect(56, 360, 400, 56),
                        "buttonWhitevsHardAI": p.Rect(56, 420, 400, 56),
                        "buttonRomanian": p.Rect(60, 20, 40, 40),
                        "buttonEnglish": p.Rect(120, 20, 40, 40),
                        "buttonGerman": p.Rect(60, 70, 40, 40),
                        "buttonRussian": p.Rect(120, 70, 40, 40),
                        "buttonSubscribe": p.Rect(466, 130, 40, 40),
                        "buttonImport": p.Rect(466, 190, 40, 40)}
        self.mainClock = p.time.Clock()
        self.font = p.font.SysFont(r'couriernew', 15)
        # SỬA ĐỔI: Thêm ../ vào đường dẫn
        programIcon = p.image.load(r'../images/mychesslogo.png')
        p.display.set_icon(programIcon)
        # SỬA LỖI: Thêm dòng này để tải hình ảnh quân cờ
        self.loadBoard()

    def loadBoard(self):
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            # SỬA ĐỔI: Thêm ../ vào đường dẫn
            self.IMAGES[piece] = p.transform.scale(p.image.load("../images/" + piece + ".png"), (self.SQUARE_SIZE, self.SQUARE_SIZE))

    def drawBoard(self):
        global colors
        colors = [p.Color(235, 235, 208), p.Color(119, 148, 85)]
        for i in range(self.n):
            for j in range(self.n):
                color = colors[((i + j) % 2)]
                p.draw.rect(self.screen, color, p.Rect(j * self.SQUARE_SIZE, i * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    def drawPieces(self, board):
        for i in range(self.n):
            for j in range(self.n):
                piece = board[i][j]
                if piece != "--":
                    self.screen.blit(self.IMAGES[piece], p.Rect(j * self.SQUARE_SIZE, i * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    def drawText(self, text):
        font = p.font.SysFont("couriernew", 22, True, False)
        textObject = font.render(text, False, p.Color("Black"))
        textLocation = p.Rect(0, 0, self.WIDTH, self.HEIGHT).move(self.WIDTH/2 - textObject.get_width()/2,
                                                        self.HEIGHT/2 - textObject.get_height()/2)
        self.screen.blit(textObject, textLocation)
        textObject = font.render(text, False, p.Color("Gray"))
        self.screen.blit(textObject, textLocation.move(2, 2))

    def saveGame(self, movesList):
        result = movesList.pop()
        turnDictionary = {}
        # Lưu ý: đường dẫn này có thể cần sửa thành '../core/last_game_logs.txt'
        # nếu bạn chạy file từ thư mục gốc.
        file = open(r"core/last_game_logs.txt", "w")
        for i in range(0, len(movesList)):
            try:
                if int(movesList[i][1]) not in turnDictionary:
                    turnDictionary[movesList[i][1]] = movesList[i][1:]+"\n"
                    file.write(movesList[i][1:]+"\n")
            except:
                pass
        file.write(result)
        file.close()

    def drawMenuText(self, text, color, x, y):
        textobj = self.font.render(text, 1, color)
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        self.screen.blit(textobj, textrect)

    def mainMenu(self, language, subscribed):
        while True and self.click == False:
            self.screen.fill(p.Color(235, 235, 208))
            # SỬA ĐỔI: Thêm ../ vào đường dẫn
            image = p.image.load(r"../images/mychesslogo.png")
            self.screen.blit(image, (216, 10))

            for button in self.buttons:
                p.draw.rect(self.screen, p.Color(119, 148, 85), self.buttons[button])

            import xml.etree.ElementTree as ET
            # Lưu ý: đường dẫn này có thể cần sửa tương tự
            mytree = ET.parse(r"../core//display.xml")
            myroot = mytree.getroot()

            k = 2
            for x in myroot.findall(language):

                restartText = x.find("restart").text
                resignText = x.find("resign").text
                undoText = x.find("undo").text
                captionText = x.find("menutext").text
                engineText = x.find("enginetext").text

                p.display.set_caption(captionText)

                self.drawMenuText(restartText, p.Color("black"), 308, 20)
                self.drawMenuText(resignText, p.Color("black"), 308, 40)
                self.drawMenuText(undoText, p.Color("black"), 308, 60)

                if subscribed:
                    self.drawMenuText(engineText, p.Color("black"), 308, 100)

                for i in x.iter():
                    font = p.font.SysFont("couriernew", 22, True, False)
                    textObject = font.render(i.text, False, p.Color("Black"))

                    if i.text != x.find("aivai").text and i.text != x.find("whitevsai").text and \
                            i.text != x.find("blackvsai").text and i.text != x.find("practice").text and \
                            i.text != x.find("aivsai2").text and i.text != x.find("whitevsai2").text:
                            pass
                    else:
                            self.drawMenuText(i.text, p.Color("black"), 56 + (abs(512 - textObject.get_width()))/ 2, 56/2 + 60 * k)
                            k = k + 1

            project_root = os.path.dirname(os.path.dirname(__file__))
            # SỬA ĐỔI: Thêm ../ vào tất cả các đường dẫn hình ảnh
            self.screen.blit(p.image.load(r"../images/romaniabutton.png"), (60, 20, 20, 40))
            self.screen.blit(p.image.load(r"../images/ukflag.png"), (120, 20, 80, 40))
            self.screen.blit(p.image.load(r"../images/germanyflag.png"), (60, 70, 40, 40))
            self.screen.blit(p.image.load(r"../images/rusflag.png"), (120, 70, 40, 40))
            self.screen.blit(p.image.load(r"../images/chessengine.png"), (466, 130, 40, 40))
            self.screen.blit(p.image.load(r"../images/importchessgame.png"), (466, 190, 40, 40))

            self.click = False
            for event in p.event.get():
                if event.type == QUIT:
                    p.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        p.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # SỬA ĐỔI: Kiểm tra xem nút nào được nhấn và trả về tên của nó
                        mx, my = p.mouse.get_pos()
                        for button_name, rect in self.buttons.items():
                            if rect.collidepoint((mx, my)):
                                return button_name  # Trả về tên nút được nhấn
                        self.click = True  # Giữ lại logic cũ nếu cần

            p.display.update()
            self.mainClock.tick(60)
