# Import các thư viện cần thiết.
import os  # Dùng để tương tác với hệ điều hành, không được sử dụng trực tiếp trong file này nhưng có thể hữu ích.

import pygame as p  # Thư viện chính để xây dựng game và giao diện đồ họa.
import sys  # Dùng để thoát chương trình một cách an toàn.
from pygame.locals import *  # Import tất cả các hằng số của Pygame (ví dụ: QUIT, KEYDOWN).


# Lớp ChessView quản lý tất cả các hoạt động liên quan đến việc hiển thị.
class ChessView():
    # Hàm khởi tạo, thiết lập các thuộc tính ban đầu cho giao diện.
    def __init__(self):
        p.init()  # Khởi tạo tất cả các module của Pygame, đây là bước bắt buộc.
        # Định nghĩa các hằng số kích thước cho cửa sổ game và các thành phần khác.
        self.WIDTH = self.HEIGHT = self.MOVE_LOG_HEIGHT = 512  # Chiều rộng và cao của bàn cờ.
        self.MOVE_LOG_WIDTH = 280  # Chiều rộng khu vực hiển thị lịch sử nước đi.
        self.EVAL_BAR_WIDTH = 50  # Chiều rộng thanh đánh giá.
        self.n = 8  # Số ô trên mỗi hàng/cột của bàn cờ.
        self.SQUARE_SIZE = self.HEIGHT // self.n  # Tính kích thước của một ô cờ.
        self.FPS = 15  # Tốc độ khung hình mỗi giây cho game.
        self.IMAGES = {}  # Từ điển để lưu trữ các hình ảnh quân cờ đã được tải.
        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))  # Tạo cửa sổ hiển thị chính.
        self.click = False  # Một biến cờ (flag), không còn được sử dụng nhiều trong phiên bản đã tối ưu.
        # Từ điển định nghĩa các vùng hình chữ nhật (Rect) cho tất cả các nút bấm trên menu.
        # p.Rect(x, y, width, height)
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
        self.mainClock = p.time.Clock()  # Tạo đối tượng Clock để kiểm soát FPS.
        self.font = p.font.SysFont(r'couriernew', 15)  # Tải font chữ mặc định cho menu.
        # Tải hình ảnh logo của chương trình.
        programIcon = p.image.load(r'../images/mychesslogo.png')
        # Đặt icon cho cửa sổ chương trình.
        p.display.set_icon(programIcon)
        # Gọi hàm để tải hình ảnh các quân cờ vào bộ nhớ.
        self.loadBoard()

    # Hàm tải và xử lý hình ảnh các quân cờ.
    def loadBoard(self):
        # Danh sách tên các tệp hình ảnh của quân cờ.
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        # Vòng lặp qua từng tên tệp.
        for piece in pieces:
            # Tải hình ảnh, thay đổi kích thước cho vừa với một ô cờ, và lưu vào từ điển IMAGES.
            self.IMAGES[piece] = p.transform.scale(p.image.load("../images/" + piece + ".png"),
                                                   (self.SQUARE_SIZE, self.SQUARE_SIZE))

    # Hàm vẽ các ô vuông của bàn cờ.
    def drawBoard(self):
        global colors  # Khai báo biến toàn cục (không phải là cách làm tốt nhất, nhưng hoạt động).
        # Định nghĩa hai màu cho các ô cờ.
        colors = [p.Color(235, 235, 208), p.Color(119, 148, 85)]
        # Vòng lặp lồng nhau để duyệt qua từng ô cờ.
        for i in range(self.n):
            for j in range(self.n):
                # Sử dụng toán tử modulo để xen kẽ màu cho các ô (tạo họa tiết bàn cờ).
                color = colors[((i + j) % 2)]
                # Vẽ một hình chữ nhật (ô cờ) với màu đã chọn tại vị trí tương ứng.
                p.draw.rect(self.screen, color,
                            p.Rect(j * self.SQUARE_SIZE, i * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

    # Hàm vẽ các quân cờ lên bàn cờ.
    def drawPieces(self, board):
        # Vòng lặp lồng nhau để duyệt qua từng ô cờ.
        for i in range(self.n):
            for j in range(self.n):
                # Lấy tên quân cờ từ mảng trạng thái bàn cờ (do Controller cung cấp).
                piece = board[i][j]
                # Nếu ô cờ không trống.
                if piece != "--":
                    # Vẽ (blit) hình ảnh quân cờ tương ứng từ từ điển IMAGES lên màn hình.
                    self.screen.blit(self.IMAGES[piece],
                                     p.Rect(j * self.SQUARE_SIZE, i * self.SQUARE_SIZE, self.SQUARE_SIZE,
                                            self.SQUARE_SIZE))

    # Hàm vẽ văn bản (ví dụ: thông báo kết thúc game) ra giữa màn hình.
    def drawText(self, text):
        font = p.font.SysFont("couriernew", 22, True, False)  # Tải font chữ lớn hơn.
        textObject = font.render(text, False, p.Color("Black"))  # Tạo đối tượng văn bản màu đen.
        # Tính toán vị trí để căn giữa văn bản trên màn hình.
        textLocation = p.Rect(0, 0, self.WIDTH, self.HEIGHT).move(self.WIDTH / 2 - textObject.get_width() / 2,
                                                                  self.HEIGHT / 2 - textObject.get_height() / 2)
        # Vẽ văn bản màu đen.
        self.screen.blit(textObject, textLocation)
        # Tạo hiệu ứng đổ bóng bằng cách vẽ lại văn bản màu xám lệch đi một chút.
        textObject = font.render(text, False, p.Color("Gray"))
        self.screen.blit(textObject, textLocation.move(2, 2))

    # Hàm lưu lịch sử ván cờ vào tệp.
    def saveGame(self, movesList):
        result = movesList.pop()  # Lấy kết quả ván cờ ra khỏi danh sách.
        turnDictionary = {}  # Từ điển để tránh ghi trùng lặp.
        # Mở tệp để ghi đè.
        file = open(r"core/last_game_logs.txt", "w")
        # Vòng lặp qua danh sách các nước đi.
        for i in range(0, len(movesList)):
            try:
                # Logic này có vẻ phức tạp và có thể không chính xác, mục đích là định dạng lại lịch sử.
                if int(movesList[i][1]) not in turnDictionary:
                    turnDictionary[movesList[i][1]] = movesList[i][1:] + "\n"
                    file.write(movesList[i][1:] + "\n")
            except:
                pass  # Bỏ qua lỗi nếu có.
        file.write(result)  # Ghi kết quả ở cuối tệp.
        file.close()  # Đóng tệp.

    # Hàm trợ giúp để vẽ văn bản cho menu tại một vị trí cụ thể.
    def drawMenuText(self, text, color, x, y):
        textobj = self.font.render(text, 1, color)  # Tạo đối tượng văn bản.
        textrect = textobj.get_rect()  # Lấy vùng chữ nhật bao quanh văn bản.
        textrect.topleft = (x, y)  # Đặt vị trí góc trên bên trái của văn bản.
        self.screen.blit(textobj, textrect)  # Vẽ văn bản lên màn hình.

    # Hàm vẽ và quản lý vòng lặp của menu chính.
    def mainMenu(self, language, subscribed):
        # Vòng lặp vô hạn, chỉ thoát khi người dùng click vào một nút (hàm sẽ return).
        while True and self.click == False:
            self.screen.fill(p.Color(235, 235, 208))  # Tô màu nền cho menu.
            # Vẽ logo của game.
            image = p.image.load(r"../images/mychesslogo.png")
            self.screen.blit(image, (216, 10))

            # Vẽ tất cả các hình chữ nhật nền cho các nút bấm.
            for button in self.buttons:
                p.draw.rect(self.screen, p.Color(119, 148, 85), self.buttons[button])

            # Import thư viện XML để đọc văn bản đa ngôn ngữ.
            import xml.etree.ElementTree as ET
            # Phân tích cú pháp tệp display.xml.
            mytree = ET.parse(r"../core//display.xml")
            myroot = mytree.getroot()

            k = 2  # Biến đếm để xác định vị trí y của các nút.
            # Tìm thẻ tương ứng với ngôn ngữ đã chọn (ví dụ: <english>).
            for x in myroot.findall(language):

                # Lấy các chuỗi văn bản từ tệp XML.
                restartText = x.find("restart").text
                resignText = x.find("resign").text
                undoText = x.find("undo").text
                captionText = x.find("menutext").text
                engineText = x.find("enginetext").text

                # Đặt tiêu đề cho cửa sổ game.
                p.display.set_caption(captionText)

                # Vẽ các văn bản hướng dẫn (R, S, Z).
                self.drawMenuText(restartText, p.Color("black"), 308, 20)
                self.drawMenuText(resignText, p.Color("black"), 308, 40)
                self.drawMenuText(undoText, p.Color("black"), 308, 60)

                # Nếu người dùng đã đăng ký, hiển thị văn bản "Evaluate moves".
                if subscribed:
                    self.drawMenuText(engineText, p.Color("black"), 308, 100)

                # Vòng lặp qua tất cả các thẻ con trong thẻ ngôn ngữ.
                for i in x.iter():
                    font = p.font.SysFont("couriernew", 22, True, False)  # Font lớn hơn cho nút.
                    textObject = font.render(i.text, False, p.Color("Black"))

                    # Lọc ra chỉ các thẻ văn bản dành cho các nút chế độ chơi.
                    if i.text != x.find("aivai").text and i.text != x.find("whitevsai").text and \
                            i.text != x.find("blackvsai").text and i.text != x.find("practice").text and \
                            i.text != x.find("aivsai2").text and i.text != x.find("whitevsai2").text:
                        pass  # Bỏ qua các thẻ không phải nút.
                    else:
                        # Tính toán tọa độ để căn giữa văn bản bên trong nút.
                        self.drawMenuText(i.text, p.Color("black"), 56 + (abs(512 - textObject.get_width())) / 2,
                                          56 / 2 + 60 * k)
                        k = k + 1  # Tăng biến đếm để vẽ nút tiếp theo ở vị trí thấp hơn.

            # Vẽ các hình ảnh icon (cờ, engine, import) lên trên các nút.
            self.screen.blit(p.image.load(r"../images/romaniabutton.png"), (60, 20, 20, 40))
            self.screen.blit(p.image.load(r"../images/ukflag.png"), (120, 20, 80, 40))
            self.screen.blit(p.image.load(r"../images/germanyflag.png"), (60, 70, 40, 40))
            self.screen.blit(p.image.load(r"../images/rusflag.png"), (120, 70, 40, 40))
            self.screen.blit(p.image.load(r"../images/chessengine.png"), (466, 130, 40, 40))
            self.screen.blit(p.image.load(r"../images/importchessgame.png"), (466, 190, 40, 40))

            self.click = False
            # Bắt đầu vòng lặp xử lý sự kiện cho menu.
            for event in p.event.get():
                if event.type == QUIT:  # Nếu người dùng nhấn nút X.
                    p.quit()
                    sys.exit()
                if event.type == KEYDOWN:  # Nếu người dùng nhấn một phím.
                    if event.key == K_ESCAPE:  # Nếu là phím ESC.
                        p.quit()
                        sys.exit()
                if event.type == MOUSEBUTTONDOWN:  # Nếu người dùng click chuột.
                    if event.button == 1:  # Nếu là chuột trái.
                        mx, my = p.mouse.get_pos()  # Lấy tọa độ chuột.
                        # Vòng lặp qua từ điển các nút đã định nghĩa.
                        for button_name, rect in self.buttons.items():
                            # Kiểm tra xem tọa độ chuột có nằm trong vùng của nút không.
                            if rect.collidepoint((mx, my)):
                                return button_name  # **QUAN TRỌNG**: Trả về tên của nút được click, thoát khỏi vòng lặp và hàm.
                        self.click = True  # Logic cũ, ít được sử dụng.

            p.display.update()  # Cập nhật toàn bộ màn hình để hiển thị các thay đổi.
            self.mainClock.tick(60)  # Giới hạn vòng lặp chạy ở 60 FPS để menu mượt mà.