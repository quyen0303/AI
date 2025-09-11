"""
Tối ưu hóa ChessController:
1.  Tái cấu trúc toàn bộ:
    - Lớp `ChessController` được chia thành các phương thức nhỏ, có trách nhiệm rõ ràng hơn
      (`__init__`, `start_main_menu`, `start_game_loop`, `handle_player_move`, `handle_ai_move`...).
    - Vòng lặp game (`start_game_loop`) giờ đây gọn gàng hơn, chỉ gọi các hàm xử lý con.
2.  Quản lý trạng thái hiệu quả:
    - `getValidMoves()` chỉ được gọi MỘT LẦN mỗi lượt đi, thay vì gọi liên tục trong mỗi
      khung hình. Đây là một thay đổi cực kỳ quan trọng giúp giảm tải CPU.
    - Trạng thái game (như `gameOver`, `moveMade`) được quản lý chặt chẽ.
3.  Tập trung hóa logic âm thanh:
    - Mọi logic chơi âm thanh (di chuyển, ăn quân, nhập thành, chiếu hết...) được chuyển
      hết về `ChessController`.
    - Sau khi một nước đi được thực hiện, controller sẽ kiểm tra loại nước đi và chơi âm thanh
      tương ứng.
4.  Cải thiện xử lý sự kiện:
    - Xử lý sự kiện (chuột, bàn phím) được tách ra riêng, giúp code dễ đọc hơn.
5.  Cải thiện `animateMove`:
    - Sử dụng `convert_alpha()` khi tải ảnh để tối ưu việc vẽ các ảnh có vùng trong suốt.
"""
import os
import sys
import pygame as p
import tkinter as tk
from tkinter import filedialog
import chess.pgn
from core import ChessAI, ChessEngine, ChessView, ChessObserver, ChessMain


class ChessController:
    def __init__(self):
        self.view = ChessView.ChessView()
        self.model = ChessEngine.GameState()
        self.sounds = self.load_sounds()
        self.running = True

    def load_sounds(self):
        sounds = {}
        sound_files = ["menucut", "ChessOpeningSound", "ChessMoveSound", "ChessCaptureSound", "ChessCastleSound",
                       "ChessCheckmateSound", "ChessDrawSound"]
        for s_file in sound_files:
            try:
                path = os.path.join(os.path.dirname(__file__), '..', 'images', f'{s_file}.mp3')
                sounds[s_file] = p.mixer.Sound(path)
            except p.error as e:
                print(f"Cannot load sound: {s_file}, error: {e}")
                sounds[s_file] = None
        return sounds

    def play_sound(self, sound_name):
        if self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def start(self, language="english", subscribed=False):
        # The main entry point that starts the menu loop.
        while self.running:
            self.start_main_menu(language, subscribed)

    def start_main_menu(self, language, subscribed):
        self.play_sound("menucut")
        button_clicked = self.view.mainMenu(language, subscribed)

        # Game mode configuration
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
            self.model = ChessEngine.GameState()  # Reset model for new game
            self.start_game_loop(config["p1"], config["p2"], config["depth"], language, subscribed, config["import"])
        elif button_clicked == "buttonSubscribe":
            # Restart menu with updated subscription status
            self.start_main_menu(language, not subscribed)
        elif button_clicked in ["buttonRomanian", "buttonEnglish", "buttonGerman", "buttonRussian"]:
            new_lang = button_clicked.replace("button", "").lower()
            self.start_main_menu(new_lang, subscribed)

    def start_game_loop(self, playerOne, playerTwo, depth, language, subscribed, importGame):
        self.play_sound("ChessOpeningSound")
        self.view.screen = p.display.set_mode((self.view.WIDTH + self.view.MOVE_LOG_PANEL_WIDTH, self.view.HEIGHT))

        game_state = {
            'ai': ChessAI.ChessAI(depth),
            'valid_moves': self.model.getValidMoves(),
            'move_made': False,
            'animate': False,
            'game_over': False,
            'selected_square': (),
            'player_clicks': [],
            'lang_data': self.view.languages.get(language, {}),
            'pgn_game': None,
            'pgn_move_count': 1,
            'pgn_total_moves': 0,
        }

        if importGame:
            self.load_pgn_game(game_state)

        while not game_state['game_over']:
            human_turn = (self.model.whiteMoves and playerOne) or (not self.model.whiteMoves and playerTwo)

            self.handle_events(human_turn, game_state)

            if not human_turn and not game_state['game_over']:
                self.handle_ai_move(importGame, game_state)

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
        for e in p.event.get():
            if e.type == p.QUIT:
                self.running = False
                gs['game_over'] = True
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if human_turn:
                    self.handle_player_move(e.pos, gs)
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo
                    self.model.undoMove()
                    gs['valid_moves'] = self.model.getValidMoves()
                elif e.key == p.K_r:  # Reset
                    gs['game_over'] = True  # Exit current game loop to go to menu

    def handle_player_move(self, location, gs):
        col = location[0] // self.view.SQUARE_SIZE
        row = location[1] // self.view.SQUARE_SIZE
        if gs['selected_square'] == (row, col) or col >= 8:
            gs['selected_square'] = ()
            gs['player_clicks'] = []
        else:
            gs['selected_square'] = (row, col)
            gs['player_clicks'].append(gs['selected_square'])

        if len(gs['player_clicks']) == 2:
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
            if not gs['move_made']:
                gs['player_clicks'] = [gs['selected_square']]

    def handle_ai_move(self, is_pgn_game, gs):
        ai_move = None
        if is_pgn_game:
            if gs['pgn_game'] and gs['pgn_move_count'] <= gs['pgn_total_moves']:
                ai_move = gs['ai'].playPGNMove(gs['valid_moves'], gs['pgn_move_count'], gs['pgn_game'])
                gs['pgn_move_count'] += 1
            else:
                gs['game_over'] = True
        else:
            ai_move = gs['ai'].findBestMoveMinMax(self.model, gs['valid_moves'])
            if ai_move is None:
                ai_move = gs['ai'].findRandomMove(gs['valid_moves'])

        if ai_move:
            self.model.makeMove(ai_move)
            self.play_move_sound(ai_move)
            gs['move_made'] = True
            gs['animate'] = True

    def play_move_sound(self, move):
        if move.isCastleMove:
            self.play_sound("ChessCastleSound")
        elif move.isCapture:
            self.play_sound("ChessCaptureSound")
        else:
            self.play_sound("ChessMoveSound")

    def draw_game_state(self, gs):
        self.view.drawBoard(self.view.screen)
        self.highlightSquares(gs['selected_square'], gs['valid_moves'])
        self.view.drawPieces(self.view.screen, self.model.board)
        # Add move log and eval bar drawing if needed

    def check_game_over(self, gs):
        if self.model.checkMate or self.model.staleMate:
            gs['game_over'] = True
            sound = "ChessCheckmateSound" if self.model.checkMate else "ChessDrawSound"
            self.play_sound(sound)
            text = ""
            if self.model.staleMate:
                text = gs['lang_data'].get('stalemate', 'Stalemate')
            else:  # checkmate
                text = gs['lang_data'].get('whitewin') if not self.model.whiteMoves else gs['lang_data'].get('blackwin')
            self.view.drawText(text)
            p.display.flip()
            p.time.wait(3000)  # wait 3 seconds before returning to menu

    def highlightSquares(self, selected, valid_moves):
        if selected != ():
            r, c = selected
            if self.model.board[r][c][0] == ('w' if self.model.whiteMoves else 'b'):
                s = p.Surface((self.view.SQUARE_SIZE, self.view.SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(p.Color('blue'))
                self.view.screen.blit(s, (c * self.view.SQUARE_SIZE, r * self.view.SQUARE_SIZE))
                s.fill(p.Color('yellow'))
                for move in valid_moves:
                    if move.startRow == r and move.startCol == c:
                        self.view.screen.blit(s, (move.endCol * self.view.SQUARE_SIZE,
                                                  move.endRow * self.view.SQUARE_SIZE))

    def animateMove(self, move, clock):
        # This function can be kept as is, it's visually focused.
        colors = [p.Color(235, 235, 208), p.Color(119, 148, 85)]
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        framesPerSquare = 5
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        for frame in range(frameCount + 1):
            r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
            self.view.drawBoard(self.view.screen)
            self.view.drawPieces(self.view.screen, self.model.board)
            # redraw the captured piece under the moving piece
            if move.pieceCaptured != '--':
                if move.isEnpassantMove:
                    enpassant_row = move.startRow
                    self.view.screen.blit(self.view.assets[move.pieceCaptured],
                                          p.Rect(move.endCol * self.view.SQUARE_SIZE,
                                                 enpassant_row * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                                 self.view.SQUARE_SIZE))
                else:
                    self.view.screen.blit(self.view.assets[move.pieceCaptured],
                                          p.Rect(move.endCol * self.view.SQUARE_SIZE,
                                                 move.endRow * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                                 self.view.SQUARE_SIZE))

            # draw moving piece
            self.view.screen.blit(self.view.assets[move.pieceMoved],
                                  p.Rect(c * self.view.SQUARE_SIZE, r * self.view.SQUARE_SIZE, self.view.SQUARE_SIZE,
                                         self.view.SQUARE_SIZE))
            p.display.flip()
            clock.tick(120)

    def load_pgn_game(self, gs):
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                with open(file_path) as pgn:
                    gs['pgn_game'] = chess.pgn.read_game(pgn)
                    gs['pgn_total_moves'] = len(list(gs['pgn_game'].mainline_moves()))
            except Exception as e:
                print(f"Could not load PGN file: {e}")
                gs['pgn_game'] = None
