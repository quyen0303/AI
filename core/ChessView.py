# Import các thư viện cần thiết.
import os
import pygame as p
import sys
from pygame.locals import *
import xml.etree.ElementTree as ET


# Lớp ChessView quản lý tất cả các hoạt động liên quan đến việc hiển thị.
class ChessView():
    def __init__(self):
        p.init()
        # --- Kích thước ---
        self.BOARD_WIDTH = self.BOARD_HEIGHT = 512
        self.EVAL_BAR_WIDTH = 24
        self.CHAT_WIDTH = 288
        self.WIDTH = self.BOARD_WIDTH + self.EVAL_BAR_WIDTH + self.CHAT_WIDTH
        self.HEIGHT = self.BOARD_HEIGHT

        # --- Hằng số Bàn cờ ---
        self.n = 8
        self.SQUARE_SIZE = self.BOARD_HEIGHT // self.n
        self.FPS = 60
        self.IMAGES = {}

        # --- Bảng màu Hiện đại ---
        self.COLORS = {
            'board_light': p.Color("#f0d9b5"), 'board_dark': p.Color("#b58863"),
            'bg_main': p.Color("#2c2a28"), 'bg_chat': p.Color("#1e1d1c"),
            'text_light': p.Color("#e0e0e0"), 'text_dark': p.Color("#3d3c3a"),
            'accent': p.Color("#6c9d4b"), 'accent_hover': p.Color("#85b964"),
            'accent_active': p.Color("#e67f22"),
            'highlight_select': p.Color(255, 255, 0, 100),
            # **MỚI:** Màu sắc mới cho chỉ báo nước đi
            'highlight_normal': p.Color(120, 120, 120, 100),  # Xám trong suốt
            'highlight_capture': p.Color(180, 0, 0, 120)  # Đỏ sẫm trong suốt
        }

        # --- Fonts ---
        try:
            self.font_button = p.font.SysFont("Helvetica", 22, bold=True)
            self.chat_font = p.font.SysFont("Arial", 16)
        except:
            self.font_button = p.font.SysFont(None, 26, bold=True)
            self.chat_font = p.font.SysFont(None, 18)

        # --- Khởi tạo Cửa sổ & Layout ---
        self.screen = p.display.set_mode((self.WIDTH, self.HEIGHT))
        self.mainClock = p.time.Clock()
        self.eval_bar_rect = p.Rect(self.BOARD_WIDTH, 0, self.EVAL_BAR_WIDTH, self.BOARD_HEIGHT)
        chat_start_x = self.BOARD_WIDTH + self.EVAL_BAR_WIDTH
        self.input_box = p.Rect(chat_start_x + 10, self.HEIGHT - 40, self.CHAT_WIDTH - 20, 32)
        self.chat_area = p.Rect(chat_start_x + 10, 10, self.CHAT_WIDTH - 20, self.HEIGHT - 60)

        # --- Tải Tài nguyên ---
        programIcon = p.image.load(r'../images/mychesslogo.png')
        p.display.set_icon(programIcon)
        self.loadBoard()

    def loadBoard(self):
        pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
        for piece in pieces:
            image_path = os.path.join(os.path.dirname(__file__), '..', 'images', f'{piece}.png')
            self.IMAGES[piece] = p.transform.scale(p.image.load(image_path), (self.SQUARE_SIZE, self.SQUARE_SIZE))

    def drawBoard(self, is_online_mode):
        self.screen.fill(self.COLORS['bg_main'])

        for r in range(self.n):
            for c in range(self.n):
                color = self.COLORS['board_light'] if (r + c) % 2 == 0 else self.COLORS['board_dark']
                p.draw.rect(self.screen, color,
                            p.Rect(c * self.SQUARE_SIZE, r * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))

        if is_online_mode:
            p.draw.rect(self.screen, p.Color("dark gray"), self.eval_bar_rect)
            chat_bg_rect = p.Rect(self.BOARD_WIDTH + self.EVAL_BAR_WIDTH, 0, self.CHAT_WIDTH, self.HEIGHT)
            p.draw.rect(self.screen, self.COLORS['bg_chat'], chat_bg_rect)

    def drawPieces(self, board):
        for r in range(self.n):
            for c in range(self.n):
                piece = board[r][c]
                if piece != "--":
                    self.screen.blit(self.IMAGES[piece],
                                     p.Rect(c * self.SQUARE_SIZE, r * self.SQUARE_SIZE, self.SQUARE_SIZE,
                                            self.SQUARE_SIZE))

    # **HÀM ĐÃ ĐƯỢC NÂNG CẤP**
    def highlightSquares(self, gs, valid_moves, sq_selected):
        if sq_selected != ():
            r, c = sq_selected
            if 0 <= r < 8 and 0 <= c < 8 and gs.board[r][c][0] == ('w' if gs.whiteMoves else 'b'):
                # 1. Tô màu ô được chọn
                s = p.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), p.SRCALPHA)
                s.fill(self.COLORS['highlight_select'])
                self.screen.blit(s, (c * self.SQUARE_SIZE, r * self.SQUARE_SIZE))

                # 2. Tạo các surface cho nước đi thường và ăn quân
                s_normal = p.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), p.SRCALPHA)
                s_normal.fill(self.COLORS['highlight_normal'])

                s_capture = p.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), p.SRCALPHA)
                s_capture.fill(self.COLORS['highlight_capture'])

                # 3. Vẽ chỉ báo cho các nước đi hợp lệ
                for move in valid_moves:
                    if move.startRow == r and move.startCol == c:
                        end_pos = (move.endCol * self.SQUARE_SIZE, move.endRow * self.SQUARE_SIZE)
                        # Nếu là nước đi ăn quân, phủ màu đỏ
                        if move.pieceCaptured != '--':
                            self.screen.blit(s_capture, end_pos)
                        # Nếu là nước đi thường, phủ màu xám
                        else:
                            self.screen.blit(s_normal, end_pos)

    def drawText(self, text):
        font = p.font.SysFont("Helvetica", 32, True, False)
        text_object = font.render(text, True, self.COLORS['text_light'])
        text_location = p.Rect(0, 0, self.BOARD_WIDTH, self.HEIGHT).move(
            self.BOARD_WIDTH / 2 - text_object.get_width() / 2,
            self.HEIGHT / 2 - text_object.get_height() / 2)
        shadow = font.render(text, True, (0, 0, 0, 100))
        self.screen.blit(shadow, text_location.move(2, 2))
        self.screen.blit(text_object, text_location)

    def drawChatUI(self, text, history, active):
        color = self.COLORS['accent'] if active else self.COLORS['text_dark']
        p.draw.rect(self.screen, self.COLORS['text_light'], self.input_box, border_radius=5)
        p.draw.rect(self.screen, color, self.input_box, 2, border_radius=5)
        text_surface = self.chat_font.render(text, True, self.COLORS['text_dark'])
        self.screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))
        y = self.chat_area.bottom - 5
        for line in reversed(history):
            try:
                words = line.split(' ')
                current_line = ""
                lines_to_render = []
                for word in words:
                    test_line = current_line + word + " "
                    if self.chat_font.size(test_line)[0] < self.chat_area.width - 10:
                        current_line = test_line
                    else:
                        lines_to_render.append(current_line)
                        current_line = word + " "
                lines_to_render.append(current_line)

                for l in reversed(lines_to_render):
                    line_surface = self.chat_font.render(l, True, self.COLORS['text_light'])
                    y -= line_surface.get_height()
                    self.screen.blit(line_surface, (self.chat_area.x + 5, y))
                    if y < self.chat_area.top: break
                if y < self.chat_area.top: break
            except Exception as e:
                print(f"Error rendering chat line: {e}")

    def drawEvaluationBar(self, score):
        max_score = 1000
        eval_normalized = max(min(score / max_score, 1), -1)
        white_advantage_height = self.BOARD_HEIGHT / 2 * (1 - eval_normalized)
        black_rect = p.Rect(self.eval_bar_rect.x, self.eval_bar_rect.y, self.EVAL_BAR_WIDTH, white_advantage_height)
        p.draw.rect(self.screen, self.COLORS['text_dark'], black_rect)
        white_rect = p.Rect(self.eval_bar_rect.x, self.eval_bar_rect.y + white_advantage_height, self.EVAL_BAR_WIDTH,
                            self.BOARD_HEIGHT - white_advantage_height)
        p.draw.rect(self.screen, self.COLORS['text_light'], white_rect)

    def draw_menu_button(self, rect, text, mouse_pos):
        is_hovered = rect.collidepoint(mouse_pos)
        color = self.COLORS['accent_hover'] if is_hovered else self.COLORS['accent']
        p.draw.rect(self.screen, (0, 0, 0, 50), rect.move(3, 3), border_radius=12)
        p.draw.rect(self.screen, color, rect, border_radius=12)
        text_surf = self.font_button.render(text, True, self.COLORS['text_light'])
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)

    def mainMenu(self, language, subscribed):
        self.screen = p.display.set_mode((self.BOARD_WIDTH, self.BOARD_HEIGHT))

        xml_path = os.path.join(os.path.dirname(__file__), 'display.xml')
        try:
            mytree = ET.parse(xml_path)
            myroot = mytree.getroot()
            lang_data = myroot.find(language)
        except (FileNotFoundError, ET.ParseError):
            print("Không thể tải tệp ngôn ngữ, sử dụng tiếng Anh mặc định.")
            xml_fallback = "<english><aivai>AI vs AI</aivai><whitevsai>Play vs AI (White)</whitevsai><blackvsai>Play vs AI (Black)</blackvsai><practice>Practice</practice><aivsai2>Strong AI vs AI</aivsai2><whitevsai2>Play vs Strong AI</whitevsai2></english>"
            lang_data = ET.fromstring(xml_fallback)

        menu_items = {
            "buttonAIvsAI": lang_data.find("aivai").text, "buttonWhitevsAI": lang_data.find("whitevsai").text,
            "buttonAIvsBlack": lang_data.find("blackvsai").text, "buttonHumanvsHuman": lang_data.find("practice").text,
            "buttonHardAIvsHardAI": lang_data.find("aivsai2").text,
            "buttonWhitevsHardAI": lang_data.find("whitevsai2").text
        }

        button_rects = {}
        y_start = 120
        for i, key in enumerate(menu_items.keys()):
            button_rects[key] = p.Rect(56, y_start + i * 60, 400, 50)

        icon_buttons = {
            "buttonSubscribe": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'chessengine.png')),
                p.Rect(self.BOARD_WIDTH - 50, 10, 40, 40)),
            "buttonImport": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'importchessgame.png')),
                p.Rect(self.BOARD_WIDTH - 50, 60, 40, 40)),
            # --- PHẦN MÃ MỚI ĐƯỢC THÊM VÀO ---
            "buttonRomanian": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'romaniabutton.png')),
                p.Rect(10, 10, 40, 40)),
            "buttonEnglish": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'ukflag.png')),
                p.Rect(60, 10, 40, 40)),
            "buttonGerman": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'germanyflag.png')),
                p.Rect(10, 60, 40, 40)),
            "buttonRussian": (
                p.image.load(os.path.join(os.path.dirname(__file__), '..', 'images', 'rusflag.png')),
                p.Rect(60, 60, 40, 40)),
        }

        while True:
            self.screen.fill(self.COLORS['bg_main'])
            mouse_pos = p.mouse.get_pos()

            logo_path = os.path.join(os.path.dirname(__file__), '..', 'images', 'mychesslogo.png')
            logo = p.image.load(logo_path)
            self.screen.blit(logo, logo.get_rect(center=(self.BOARD_WIDTH / 2, 60)))

            for key, text in menu_items.items():
                self.draw_menu_button(button_rects[key], text, mouse_pos)

            for key, (img, rect) in icon_buttons.items():
                is_hovered = rect.collidepoint(mouse_pos)
                is_active = (key == "buttonSubscribe" and subscribed)

                if is_active:
                    bg_color = self.COLORS['accent_active']
                else:
                    bg_color = self.COLORS['accent_hover'] if is_hovered else self.COLORS['accent']
                p.draw.rect(self.screen, bg_color, rect, border_radius=5)
                self.screen.blit(img, rect)

            for event in p.event.get():
                if event.type == QUIT: p.quit(); sys.exit()
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    for key, rect in button_rects.items():
                        if rect.collidepoint(mouse_pos): return key
                    for key, (_, rect) in icon_buttons.items():
                        if rect.collidepoint(mouse_pos): return key

            p.display.update()
            self.mainClock.tick(self.FPS)


    def drawMoveHistoryPanel(self, move_history, is_online_mode=False, chat_text="", chat_history=None,
                                 chat_active=False):
            """
            Vẽ bảng điều khiển bên phải, hiển thị lịch sử nước đi.
            Nếu ở chế độ online, sẽ hiển thị thêm cả phòng chat.
            """
            if chat_history is None:
                chat_history = []

            panel_start_x = self.BOARD_WIDTH + self.EVAL_BAR_WIDTH
            panel_rect = p.Rect(panel_start_x, 0, self.CHAT_WIDTH, self.HEIGHT)
            p.draw.rect(self.screen, self.COLORS['bg_chat'], panel_rect)

            # --- Thiết lập khu vực vẽ ---
            history_area_height_ratio = 0.45 if is_online_mode else 1.0  # Chiếm toàn bộ nếu offline
            history_area = p.Rect(panel_start_x + 10, 10, self.CHAT_WIDTH - 20,
                                  self.HEIGHT * history_area_height_ratio - 20)

            # --- Logic vẽ Lịch sử nước đi (chung cho cả 2 chế độ) ---
            full_log_string = ""
            for i in range(len(move_history)):
                if i % 2 == 0:
                    full_log_string += f"{i // 2 + 1}. {move_history[i].getChessNotation()} "
                else:
                    full_log_string += f"{move_history[i].getChessNotation()} "

            words = full_log_string.split(' ')
            lines_to_render = []
            current_line = ""
            for word in words:
                if not word: continue
                test_line = current_line + word + " "
                if self.chat_font.size(test_line)[0] < history_area.width:
                    current_line = test_line
                else:
                    lines_to_render.append(current_line)
                    current_line = word + " "
            lines_to_render.append(current_line)

            y = history_area.y
            line_height = self.chat_font.get_height()
            for line in lines_to_render:
                if y < history_area.bottom - line_height:
                    line_surface = self.chat_font.render(line, True, self.COLORS['text_light'])
                    self.screen.blit(line_surface, (history_area.x, y))
                    y += line_height
                else:
                    break

            # --- Logic vẽ Phòng Chat (chỉ dành cho chế độ online) ---
            if is_online_mode:
                chat_history_area = p.Rect(panel_start_x + 10, history_area.bottom + 10, self.CHAT_WIDTH - 20,
                                           self.HEIGHT * 0.55 - 50)

                y_chat = chat_history_area.bottom - 5
                for line in reversed(chat_history):
                    try:
                        words_chat = line.split(' ')
                        current_line_chat = ""
                        lines_to_render_chat = []
                        for word_chat in words_chat:
                            test_line_chat = current_line_chat + word_chat + " "
                            if self.chat_font.size(test_line_chat)[0] < chat_history_area.width:
                                current_line_chat = test_line_chat
                            else:
                                lines_to_render_chat.append(current_line_chat)
                                current_line_chat = word_chat + " "
                        lines_to_render_chat.append(current_line_chat)

                        for l_chat in reversed(lines_to_render_chat):
                            line_surface_chat = self.chat_font.render(l_chat, True, self.COLORS['text_light'])
                            y_chat -= line_surface_chat.get_height()
                            if y_chat < chat_history_area.top: break
                            self.screen.blit(line_surface_chat, (chat_history_area.x + 5, y_chat))
                        if y_chat < chat_history_area.top: break
                    except Exception as e:
                        print(f"Error rendering chat line: {e}")

                # Vẽ Hộp nhập liệu Chat
                color = self.COLORS['accent'] if chat_active else self.COLORS['text_dark']
                p.draw.rect(self.screen, self.COLORS['text_light'], self.input_box, border_radius=5)
                p.draw.rect(self.screen, color, self.input_box, 2, border_radius=5)
                text_surface = self.chat_font.render(chat_text, True, self.COLORS['text_dark'])
                self.screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))