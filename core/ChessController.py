"""
Phiên bản tối ưu hóa của ChessController.
- Tái cấu trúc, chia nhỏ các phương thức.
- Quản lý trạng thái hiệu quả, getValidMoves() chỉ gọi một lần mỗi lượt.
- Tập trung hóa logic âm thanh và xử lý sự kiện.
- Sửa lỗi và cải thiện animateMove.
"""
import os
import sys
import pygame as p
import tkinter as tk
from tkinter import filedialog
import chess.pgn
import xml.etree.ElementTree as ET

from core import ChessAI, ChessEngine, ChessView


class ChessController:
    def __init__(self):
        self.view = ChessView.ChessView()
        self.model = ChessEngine.GameState()
        self.sounds = self.load_sounds()
        self.running = True

    def load_sounds(self):
        """Tải tất cả các tệp âm thanh cần thiết."""
        sounds = {}
        sound_files = ["menucut", "ChessOpeningSound", "ChessMoveSound", "ChessCaptureSound", "ChessCastleSound",
                       "ChessCheckmateSound", "ChessDrawSound"]
        for s_file in sound_files:
            try:
                # Đường dẫn tương đối từ thư mục core -> thư mục gốc -> images
                path = os.path.join(os.path.dirname(__file__), '..', 'images', f'{s_file}.mp3')
                sounds[s_file] = p.mixer.Sound(path)
            except p.error as e:
                print(f"Lỗi: Không thể tải âm thanh '{s_file}': {e}")
                sounds[s_file] = None
        return sounds

    def play_sound(self, sound_name):
        """Phát một âm thanh nếu nó đã được tải thành công."""
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def _load_language_data(self, language):
        """Hàm trợ giúp để đọc dữ liệu ngôn ngữ từ tệp XML."""
        try:
            path = os.path.join(os.path.dirname(__file__), 'display.xml')
            mytree = ET.parse(path)
            myroot = mytree.getroot()
            lang_node = myroot.find(language)
            if lang_node is not None:
                return {child.tag: child.text.strip() for child in lang_node}
        except (ET.ParseError, FileNotFoundError) as e:
            print(f"Lỗi: Không thể đọc tệp ngôn ngữ: {e}")
        return {} # Trả về từ điển rỗng nếu có lỗi

    def start(self, language="english", subscribed=False):
        """Vòng lặp chính của ứng dụng, bắt đầu bằng menu."""
        while self.running:
            self.start_main_menu(language, subscribed)

    def start_main_menu(self, language, subscribed):
        """Hiển thị menu chính và xử lý lựa chọn của người dùng."""
        self.view.screen = p.display.set_mode((self.view.WIDTH, self.view.HEIGHT))
        self.play_sound("menucut")
        # Hàm mainMenu giờ sẽ trả về tên của nút được nhấn
        button_clicked = self.view.mainMenu(language, subscribed)

        game_modes = {
            "buttonAIvsAI": {"p1": False, "p2": False, "depth": 2, "import": False},
            "buttonWhitevsAI": {"p1": True, "p2": False, "depth": 2, "import": False},
            "buttonAIvsBlack": {"p1": False, "p2": True, "depth": 2, "import": False},
            "buttonHumanvsHuman": {"p1": True, "p2": True, "depth": 2, "import": False},
            "buttonHardAIvsHardAI": {"p1": False, "p2": False, "depth": 3, "import": False},
            "buttonWhitevsHardAI": {"p1": True, "p2": False, "depth": 3, "import": False},
            "buttonImport": {"p1": False, "p2": False, "depth": 2, "import": True}
        }

        if button_clicked in game_modes:
            config = game_modes[button_clicked]
            self.model = ChessEngine.GameState()  # Tạo ván cờ mới
            self.start_game_loop(config["p1"], config["p2"], config["depth"], language, subscribed, config["import"])
        elif button_clicked == "buttonSubscribe":
            self.start_main_menu(language, not subscribed) # Tải lại menu với trạng thái mới
        elif button_clicked in ["buttonRomanian", "buttonEnglish", "buttonGerman", "buttonRussian"]:
            new_lang = button_clicked.replace("button", "").lower()
            self.start_main_menu(new_lang, subscribed)

    def start_game_loop(self, playerOne, playerTwo, depth, language, subscribed, importGame):
        """Vòng lặp chính của ván cờ."""
        self.play_sound("ChessOpeningSound")
        self.view.screen = p.display.set_mode((self.view.WIDTH + self.view.MOVE_LOG_WIDTH, self.view.HEIGHT))

        game_state = {
            'ai': ChessAI.ChessAI(depth),
            'valid_moves': self.model.getValidMoves(),
            'move_made': False,
            'animate': False,
            'game_over': False,
            'selected_square': (),
            'player_clicks': [],
            'lang_data': self._load_language_data(language),
            'pgn_game': None,
            'pgn_move_count': 1,
            'pgn_total_moves': 0,
        }

        if importGame:
            self.load_pgn_game(game_state)

        while self.running and not game_state['game_over']:
            human_turn = (self.model.whiteMoves and playerOne) or (not self.model.whiteMoves and playerTwo)

            self.handle_events(human_turn, game_state)

            # Lượt đi của AI
            if not human_turn and not game_state['game_over']:
                self.handle_ai_move(importGame, game_state)

            # Cập nhật sau khi một nước đi được thực hiện
            if game_state['move_made']:
                if game_state['animate']:
                    self.animateMove(self.model.moveHistory[-1], self.view.mainClock)

                game_state['valid_moves'] = self.model.getValidMoves()
                game_state['move_made'] = False
                game_state['animate'] = False

            self.draw_game_state(game_state)
            self.check_game_over(game_state)

            self.view.mainClock.tick(self.view.FPS)
            p.display.flip()

    def handle_events(self, human_turn, gs):
        """Xử lý các sự kiện từ người dùng (chuột, bàn phím)."""
        for e in p.event.get():
            if e.type == p.QUIT:
                self.running = False
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if human_turn and not gs['game_over']:
                    self.handle_player_move(e.pos, gs)
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo
                    self.model.undoMove()
                    gs['valid_moves'] = self.model.getValidMoves()
                    gs['animate'] = False
                    gs['move_made'] = False # Đặt lại trạng thái
                elif e.key == p.K_r:  # Reset
                    gs['game_over'] = True  # Thoát vòng lặp game để quay về menu

    def handle_player_move(self, location, gs):
        """Xử lý logic 2 lần nhấp chuột của người chơi."""
        col = location[0] // self.view.SQUARE_SIZE
        row = location[1] // self.view.SQUARE_SIZE
        if gs['selected_square'] == (row, col) or col >= 8: # Bỏ chọn ô
            gs['selected_square'] = ()
            gs['player_clicks'] = []
        else:
            gs['selected_square'] = (row, col)
            gs['player_clicks'].append(gs['selected_square'])

        if len(gs['player_clicks']) == 2: # Thực hiện nước đi
            move = ChessEngine.Move(gs['player_clicks'][0], gs['player_clicks'][1], self.model.board)
            for valid_move in gs['valid_moves']:
                if move == valid_move:
                    self.model.makeMove(valid_move)
                    self.play_move_sound(valid_move)
                    gs['move_made'] = True
                    gs['animate'] = True
                    gs['selected_square'] = ()
                    gs['player_clicks'] = []
                    break
            if not gs['move_made']: # Nếu nước đi không hợp lệ
                gs['player_clicks'] = [gs['selected_square']]

    def handle_ai_move(self, is_pgn_game, gs):
        """Tìm và thực hiện nước đi cho AI."""
        ai_move = None
        if is_pgn_game:
            if gs['pgn_game'] and gs['pgn_move_count'] <= gs['pgn_total_moves']:
                ai_move = gs['ai'].playPGNMove(gs['valid_moves'], gs['pgn_move_count'], gs['pgn_game'])
                gs['pgn_move_count'] += 1
            else:
                gs['game_over'] = True
        else:
            ai_move = gs['ai'].findBestMoveMinMax(self.model, gs['valid_moves'])
            if ai_move is None: # Dự phòng nếu AI không tìm được nước đi
                ai_move = gs['ai'].findRandomMove(gs['valid_moves'])

        if ai_move:
            self.model.makeMove(ai_move)
            self.play_move_sound(ai_move)
            gs['move_made'] = True
            gs['animate'] = True

    def play_move_sound(self, move):
        """Phát âm thanh phù hợp với loại nước đi."""
        if self.model.checkMate:
             self.play_sound("ChessCheckmateSound")
        elif move.isCastleMove:
            self.play_sound("ChessCastleSound")
        elif move.isCapture:
            self.play_sound("ChessCaptureSound")
        else:
            self.play_sound("ChessMoveSound")

    def draw_game_state(self, gs):
        """Vẽ toàn bộ trạng thái hiện tại của bàn cờ."""
        self.view.drawBoard()
        self.highlightSquares(gs['selected_square'], gs['valid_moves'])
        self.view.drawPieces(self.model.board)
        # TODO: Thêm logic vẽ move log và thanh đánh giá nếu cần

    def check_game_over(self, gs):
        """Kiểm tra và hiển thị thông báo kết thúc ván cờ."""
        if self.model.checkMate or self.model.staleMate:
            gs['game_over'] = True
            text = ""
            if self.model.staleMate:
                self.play_sound("ChessDrawSound")
                text = gs['lang_data'].get('stalemate', 'Stalemate')
            else: # Chiếu hết
                text = gs['lang_data'].get('blackwin') if self.model.whiteMoves else gs['lang_data'].get('whitewin')

            self.view.drawText(text)
            p.display.flip()
            p.time.wait(4000)  # Chờ 4 giây trước khi quay về menu

    def highlightSquares(self, selected, valid_moves):
        """Tô sáng ô được chọn và các nước đi hợp lệ."""
        if selected != ():
            r, c = selected
            if self.model.board[r][c][0] == ('w' if self.model.whiteMoves else 'b'):
                # Tô màu xanh cho ô đã chọn
                s = p.Surface((self.view.SQUARE_SIZE, self.view.SQUARE_SIZE))
                s.set_alpha(100)  # Độ trong suốt
                s.fill(p.Color('blue'))
                self.view.screen.blit(s, (c * self.view.SQUARE_SIZE, r * self.view.SQUARE_SIZE))

                # Tô màu vàng cho các ô có thể di chuyển đến
                s.fill(p.Color('yellow'))
                for move in valid_moves:
                    if move.startRow == r and move.startCol == c:
                        self.view.screen.blit(s, (move.endCol * self.view.SQUARE_SIZE, move.endRow * self.view.SQUARE_SIZE))

    def animateMove(self, move, clock):
        """Vẽ hiệu ứng di chuyển quân cờ."""
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        framesPerSquare = 5
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare

        for frame in range(frameCount + 1):
            # r và c là giá trị float để tạo hiệu ứng mượt mà
            r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)

            # Vẽ lại bàn cờ nền
            self.view.drawBoard()
            self.view.drawPieces(self.model.board)

            # Vẽ lại quân cờ bị ăn dưới quân cờ đang di chuyển
            if move.pieceCaptured != '--':
                if move.isEnpassantMove:
                    enpassant_row = move.startRow
                    enpassant_col = move.endCol
                    # SỬA LỖI: Thêm width và height vào p.Rect()
                    self.view.screen.blit(self.view.IMAGES[move.pieceCaptured],
                                          p.Rect(enpassant_col * self.view.SQUARE_SIZE,
                                                 enpassant_row * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                                 self.view.SQUARE_SIZE))
                else:
                    # SỬA LỖI: Thêm width và height vào p.Rect()
                    self.view.screen.blit(self.view.IMAGES[move.pieceCaptured],
                                          p.Rect(move.endCol * self.view.SQUARE_SIZE,
                                                 move.endRow * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                                 self.view.SQUARE_SIZE))

            # Vẽ quân cờ đang di chuyển
            # SỬA LỖI: Thêm width và height vào p.Rect()
            self.view.screen.blit(self.view.IMAGES[move.pieceMoved],
                                  p.Rect(c * self.view.SQUARE_SIZE, r * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                         self.view.SQUARE_SIZE))

            p.display.flip()
            clock.tick(120)

    def load_pgn_game(self, gs):
        """Mở hộp thoại để chọn và tải tệp PGN."""
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Portable Game Notation", "*.pgn")])
        if file_path:
            try:
                with open(file_path) as pgn:
                    gs['pgn_game'] = chess.pgn.read_game(pgn)
                    if gs['pgn_game']:
                        gs['pgn_total_moves'] = len(list(gs['pgn_game'].mainline_moves()))
                    else:
                        print("Lỗi: Không thể đọc game từ tệp PGN.")
                        gs['pgn_game'] = None
            except Exception as e:
                print(f"Lỗi: Không thể tải tệp PGN: {e}")
                gs['pgn_game'] = None