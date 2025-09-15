import os
import sys
import pygame as p
import tkinter as tk
from tkinter import filedialog
import chess.pgn
import xml.etree.ElementTree as ET
from collections import deque

from core import ChessAI, ChessEngine, ChessView


# Lớp ChessController đóng vai trò là "bộ não" trung tâm của ứng dụng, theo kiến trúc MVC.
# Nó kết nối logic game (Model), giao diện người dùng (View), và AI,
# đồng thời quản lý luồng chính của chương trình (vòng lặp game, sự kiện).
class ChessController:
    # --- 1. KHỞI TẠO VÀ CẤU TRÚC ---
    def __init__(self, client_handler=None):
        """
        Hàm khởi tạo của Controller. Sẽ được chạy đầu tiên khi một đối tượng ChessController được tạo.
        - Khởi tạo các thành phần cốt lõi: View (Giao diện), Model (Logic game).
        - Tải các tài nguyên cần thiết như âm thanh.
        - Thiết lập trạng thái ban đầu của ứng dụng.
        - client_handler: Một đối tượng Client để xử lý kết nối mạng.
                         Nếu là None, game sẽ chạy ở chế độ offline.
        """
        self.view = ChessView.ChessView()  # Tạo một đối tượng View để xử lý việc vẽ.
        self.model = ChessEngine.GameState()  # Tạo một đối tượng Model để quản lý trạng thái game.
        self.sounds = self.load_sounds()  # Tải tất cả các file âm thanh.
        self.running = True  # Cờ điều khiển vòng lặp chính của ứng dụng.
        self.client = client_handler  # Lưu trữ đối tượng client để phân biệt online/offline.

    def load_sounds(self):
        """Tải tất cả các tệp âm thanh cần thiết vào một từ điển khi khởi động."""
        sounds = {}
        sound_files = ["menucut", "ChessOpeningSound", "ChessMoveSound", "ChessCaptureSound", "ChessCastleSound",
                       "ChessCheckmateSound", "ChessDrawSound"]
        for s_file in sound_files:
            try:
                # Tạo đường dẫn chính xác đến file âm thanh
                path = os.path.join(os.path.dirname(__file__), '..', 'images', f'{s_file}.mp3')
                sounds[s_file] = p.mixer.Sound(path)
            except p.error as e:
                print(f"Lỗi: Không thể tải âm thanh '{s_file}': {e}")
                sounds[s_file] = None  # Nếu lỗi, không có âm thanh
        return sounds

    def play_sound(self, sound_name):
        """Phát một âm thanh từ từ điển đã tải nếu nó tồn tại."""
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def _load_language_data(self, language):
        """Hàm trợ giúp để đọc dữ liệu ngôn ngữ từ tệp display.xml và trả về một từ điển."""
        try:
            path = os.path.join(os.path.dirname(__file__), 'display.xml')
            mytree = ET.parse(path)
            myroot = mytree.getroot()
            lang_node = myroot.find(language)
            # Trả về một từ điển dạng {'thẻ_xml': 'nội_dung'}
            return {child.tag: child.text.strip() for child in lang_node} if lang_node is not None else {}
        except (ET.ParseError, FileNotFoundError):
            return {}  # Trả về từ điển rỗng nếu có lỗi

    # --- 2. VÒNG LẶP CHÍNH CỦA ỨNG DỤNG ---
    def start(self, language="english", subscribed=False):
        """
        Điểm khởi đầu chính của controller, bắt đầu vòng lặp menu.
        Vòng lặp này sẽ chạy liên tục, đảm bảo chương trình luôn quay về menu sau mỗi ván cờ.
        """
        while self.running:
            self.start_main_menu(language, subscribed)

    def start_main_menu(self, language, subscribed):
        """
        Hiển thị menu chính và chờ lựa chọn của người dùng.
        Dựa trên lựa chọn, nó sẽ cấu hình và bắt đầu một ván cờ mới hoặc thay đổi cài đặt.
        """
        self.play_sound("menucut")
        # Gọi View để vẽ menu và nhận lại nút đã được bấm
        button_clicked = self.view.mainMenu(language, subscribed)

        # Từ điển chứa cấu hình cho các chế độ chơi khác nhau.
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
            self.model = ChessEngine.GameState()  # Tạo lại model để bắt đầu ván cờ mới.
            self.start_game_loop(config["p1"], config["p2"], config["depth"], language, subscribed, config["import"])
        elif button_clicked == "buttonSubscribe":
            # Tải lại menu với trạng thái 'subscribed' được đảo ngược.
            self.start_main_menu(language, not subscribed)
        elif button_clicked in ["buttonRomanian", "buttonEnglish", "buttonGerman", "buttonRussian"]:
            # Nếu người dùng chọn lá cờ, thay đổi ngôn ngữ và tải lại menu
            new_lang = button_clicked.replace("button", "").lower()
            self.start_main_menu(new_lang, subscribed)

    def start_game_loop(self, playerOne, playerTwo, depth, language, subscribed, importGame):
        """
        Vòng lặp chính của một ván cờ.
        Quản lý trạng thái, xử lý sự kiện, và cập nhật giao diện trong suốt ván đấu.
        """
        self.play_sound("ChessOpeningSound")
        is_online_mode = self.client is not None
        # Luôn khởi tạo màn hình với chiều rộng đầy đủ để hiển thị thanh bên.
        self.view.screen = p.display.set_mode((self.view.WIDTH, self.view.HEIGHT))

        # 'game_state': một từ điển lớn để theo dõi mọi thứ trong ván cờ hiện tại.
        game_state = {
            'ai': ChessAI.ChessAI(depth), 'valid_moves': self.model.getValidMoves(), 'move_made': False,
            'animate': False, 'game_over': False, 'selected_square': (), 'player_clicks': [],
            'lang_data': self._load_language_data(language), 'pgn_game': None, 'pgn_move_count': 1,
            'pgn_total_moves': 0, 'chat_input_active': False, 'chat_input_text': '',
            'subscribed': subscribed, 'current_score': 0
        }

        if importGame: self.load_pgn_game(game_state)
        if game_state['subscribed']:
            game_state['current_score'] = game_state['ai'].scoreBoard(self.model)

        # Vòng lặp chính của ván cờ, chạy cho đến khi game kết thúc.
        while self.running and not game_state['game_over']:
            # Xác định xem có phải lượt của người chơi hay không
            human_turn = (self.model.whiteMoves and playerOne) or (not self.model.whiteMoves and playerTwo)

            self.handle_events(human_turn, game_state)  # Luôn lắng nghe sự kiện

            if not human_turn and not game_state['game_over']:  # Nếu đến lượt máy
                self.handle_ai_move(importGame, game_state)

            if game_state['move_made']:  # Nếu một nước đi vừa được thực hiện
                if game_state['animate']:
                    self.animateMove(self.model.moveHistory[-1], self.view.mainClock, game_state)
                game_state['valid_moves'] = self.model.getValidMoves()
                game_state['move_made'] = False
                game_state['animate'] = False
                if game_state['subscribed']:
                    game_state['current_score'] = game_state['ai'].scoreBoard(self.model)

            self.draw_game_state(game_state, is_online_mode)  # Vẽ lại toàn bộ giao diện
            self.check_game_over(game_state)  # Kiểm tra kết thúc ván cờ

            self.view.mainClock.tick(self.view.FPS)  # Giới hạn tốc độ khung hình
            p.display.flip()  # Cập nhật màn hình

    # --- 3. XỬ LÝ SỰ KIỆN VÀ NƯỚC ĐI ---
    def handle_events(self, human_turn, gs):
        """Xử lý tất cả các tương tác từ người dùng (chuột, bàn phím)."""
        for e in p.event.get():
            if e.type == p.QUIT:  # Nếu người dùng đóng cửa sổ
                self.running = False;
                p.quit();
                sys.exit()

            if e.type == p.MOUSEBUTTONDOWN:
                # Phân biệt giữa việc click vào hộp chat và click vào bàn cờ.
                if self.client and self.view.input_box.collidepoint(e.pos):
                    gs['chat_input_active'] = True
                else:
                    gs['chat_input_active'] = False

                # Nếu là lượt người chơi và không click vào chat, xử lý nước đi
                if not gs['chat_input_active'] and human_turn and not gs['game_over']:
                    self.handle_player_move(e.pos, gs)

            if e.type == p.KEYDOWN:
                # Nếu hộp chat đang được kích hoạt, nhận dữ liệu gõ phím.
                if gs['chat_input_active']:
                    if e.key == p.K_RETURN:  # Gửi tin nhắn
                        if self.client and gs['chat_input_text']:
                            self.client.send_chat_message(gs['chat_input_text'])
                        gs['chat_input_text'] = ''
                    elif e.key == p.K_BACKSPACE:  # Xóa ký tự
                        gs['chat_input_text'] = gs['chat_input_text'][:-1]
                    else:
                        gs['chat_input_text'] += e.unicode
                # Nếu không, xử lý các phím tắt cho game.
                else:
                    if e.key == p.K_z:  # Phím Z: Hoàn tác
                        self.model.undoMove();
                        gs['valid_moves'] = self.model.getValidMoves();
                        gs['animate'] = False;
                        gs['move_made'] = False
                    elif e.key == p.K_r:  # Phím R: Quay về menu
                        gs['game_over'] = True
                    elif e.key == p.K_s and human_turn:  # Phím S: Đầu hàng
                        gs['game_over'] = True
                        gs['resigned'] = True  # Đặt cờ báo hiệu đầu hàng

    def handle_player_move(self, location, gs):
        """Xử lý logic 2 lần nhấp chuột của người chơi để thực hiện nước đi."""
        col = location[0] // self.view.SQUARE_SIZE
        row = location[1] // self.view.SQUARE_SIZE
        if gs['selected_square'] == (row, col) or col >= 8:  # Hủy chọn nếu click lại hoặc click ngoài bàn cờ
            gs['selected_square'] = ();
            gs['player_clicks'] = []
        else:
            gs['selected_square'] = (row, col);
            gs['player_clicks'].append(gs['selected_square'])

        if len(gs['player_clicks']) == 2:  # Khi đã có đủ 2 lần nhấp (chọn quân và chọn ô đến)
            move = ChessEngine.Move(gs['player_clicks'][0], gs['player_clicks'][1], self.model.board)
            for valid_move in gs['valid_moves']:
                if move == valid_move:  # Nếu nước đi hợp lệ
                    self.model.makeMove(valid_move);
                    self.play_move_sound(valid_move)
                    gs.update({'move_made': True, 'animate': True, 'selected_square': (), 'player_clicks': []})
                    return  # Thoát sau khi tìm thấy nước đi hợp lệ
            # Nếu nước đi không hợp lệ, giữ lại lần nhấp cuối cùng
            gs['player_clicks'] = [gs['selected_square']]

    def handle_ai_move(self, is_pgn_game, gs):
        """Gọi AI để tìm và thực hiện nước đi."""
        ai_move = None
        if is_pgn_game:  # Nếu đang ở chế độ xem lại từ file PGN
            if gs['pgn_game'] and gs['pgn_move_count'] <= gs['pgn_total_moves']:
                ai_move = gs['ai'].playPGNMove(gs['valid_moves'], gs['pgn_move_count'], gs['pgn_game'])
                gs['pgn_move_count'] += 1
            else:
                gs['game_over'] = True  # Hết ván cờ PGN
        else:  # Nếu là chế độ chơi bình thường với AI
            ai_move = gs['ai'].findBestMoveMinMax(self.model, gs['valid_moves'])

        if ai_move is None and not is_pgn_game:  # Dự phòng nếu AI không tìm được nước đi
            ai_move = gs['ai'].findRandomMove(gs['valid_moves'])

        if ai_move:  # Nếu tìm được nước đi
            self.model.makeMove(ai_move);
            self.play_move_sound(ai_move)
            gs.update({'move_made': True, 'animate': True})

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

    # --- 4. HIỂN THỊ VÀ GIAO DIỆN ---
    def draw_game_state(self, gs, is_online_mode):
        """
        Hàm tổng hợp, ra lệnh cho View vẽ toàn bộ trạng thái hiện tại của bàn cờ và giao diện.
        """
        self.view.drawBoard(is_online_mode)
        self.view.highlightSquares(self.model, gs['valid_moves'], gs['selected_square'])
        self.view.drawPieces(self.model.board)

        if gs['subscribed']:
            self.view.drawEvaluationBar(gs['current_score'])

        # Gọi hàm hợp nhất để vẽ thanh bên cho cả hai chế độ
        if is_online_mode:
            with self.client.chat_lock:
                history_copy = list(self.client.chat_history)
            self.view.drawMoveHistoryPanel(self.model.moveHistory, is_online_mode=True,
                                           chat_text=gs['chat_input_text'], chat_history=history_copy,
                                           chat_active=gs['chat_input_active'])
        else:  # Chế độ offline
            self.view.drawMoveHistoryPanel(self.model.moveHistory, is_online_mode=False)

    def check_game_over(self, gs):
        """Kiểm tra và hiển thị thông báo kết thúc ván cờ (chiếu hết, hòa, hoặc đầu hàng)."""
        game_ended = False
        text = ""

        if gs.get('resigned', False):  # Kiểm tra cờ đầu hàng
            game_ended = True
            text = gs['lang_data'].get('humanresign', 'Player resigned')
        elif self.model.checkMate or self.model.staleMate:  # Kiểm tra chiếu hết hoặc hòa
            game_ended = True
            text = gs['lang_data'].get('stalemate') if self.model.staleMate else (
                gs['lang_data'].get('blackwin') if self.model.whiteMoves else gs['lang_data'].get('whitewin'))

        if game_ended:
            gs['game_over'] = True
            self.save_game_log()  # Lưu lịch sử ván đấu
            if text: self.view.drawText(text)  # Hiển thị thông báo
            p.display.flip()

            # Vòng lặp chờ người dùng nhấp chuột để quay về menu
            waiting_for_input = True
            while waiting_for_input:
                for e in p.event.get():
                    if e.type == p.QUIT:
                        self.running = False;
                        waiting_for_input = False;
                        p.quit();
                        sys.exit()
                    if e.type == p.MOUSEBUTTONDOWN:
                        waiting_for_input = False
                self.view.mainClock.tick(15)  # Giảm tải CPU khi chờ

    def save_game_log(self):
        """
        Lưu lịch sử các nước đi của ván cờ vừa kết thúc vào file last_game_logs.txt.
        """
        file_path = os.path.join(os.path.dirname(__file__), 'last_game_logs.txt')
        try:
            with open(file_path, "w") as f:
                log_string = ""
                for i in range(0, len(self.model.moveHistory), 2):
                    move_number = i // 2 + 1
                    white_move = self.model.moveHistory[i].getChessNotation()
                    log_string += f"{move_number}. {white_move}"
                    if (i + 1) < len(self.model.moveHistory):
                        black_move = self.model.moveHistory[i + 1].getChessNotation()
                        log_string += f" {black_move}\n"
                    else:
                        log_string += "\n"
                f.write(log_string)

                # Xác định và ghi kết quả ván cờ
                result = "1/2-1/2"  # Hòa cờ (Stalemate)
                if self.model.checkMate:
                    result = "0-1" if self.model.whiteMoves else "1-0"
                f.write(f"result: {result}\n")
        except IOError as e:
            print(f"Could not write to game log file: {e}")

    def animateMove(self, move, clock, game_state):
        """Vẽ hiệu ứng di chuyển quân cờ một cách mượt mà."""
        dR, dC = move.endRow - move.startRow, move.endCol - move.startCol
        framesPerSquare = 5
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        for frame in range(frameCount + 1):
            r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
            self.draw_game_state(game_state, self.client is not None)

            # Xóa quân cờ ở ô cũ để tạo hiệu ứng di chuyển.
            color = self.view.COLORS['board_light'] if (move.startRow + move.startCol) % 2 == 0 else self.view.COLORS[
                'board_dark']
            p.draw.rect(self.view.screen, color,
                        p.Rect(move.startCol * self.view.SQUARE_SIZE, move.startRow * self.view.SQUARE_SIZE,
                               self.view.SQUARE_SIZE, self.view.SQUARE_SIZE))

            # Vẽ lại quân cờ bị ăn (nếu có) để quân di chuyển đè lên trên.
            if move.pieceCaptured != '--':
                self.view.screen.blit(self.view.IMAGES[move.pieceCaptured],
                                      p.Rect(move.endCol * self.view.SQUARE_SIZE, move.endRow * self.view.SQUARE_SIZE,
                                             self.view.SQUARE_SIZE, self.view.SQUARE_SIZE))

            # Vẽ quân cờ đang di chuyển tại vị trí được nội suy.
            self.view.screen.blit(self.view.IMAGES[move.pieceMoved],
                                  p.Rect(c * self.view.SQUARE_SIZE, r * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                         self.view.SQUARE_SIZE))

            p.display.flip()
            clock.tick(120)

    def load_pgn_game(self, gs):
        """Mở hộp thoại để người dùng chọn và tải tệp PGN."""
        root = tk.Tk();
        root.withdraw()  # Ẩn cửa sổ tkinter rỗng
        file_path = filedialog.askopenfilename(filetypes=[("Portable Game Notation", "*.pgn")])
        if file_path:
            try:
                with open(file_path) as pgn:
                    game = chess.pgn.read_game(pgn)
                    if game: gs.update({'pgn_game': game, 'pgn_total_moves': len(list(game.mainline_moves()))})
            except Exception as e:
                print(f"Lỗi PGN: {e}")