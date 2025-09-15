# Import các thư viện cần thiết.
import socket
import pygame as p
import threading
from abc import ABCMeta
import datetime
from collections import deque
from core import ChessController
import os # <-- THÊM DÒNG NÀY

# --- Cấu hình mạng cho Client ---
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

# Lớp cơ sở trừu tượng (Interface)
class IClient(metaclass=ABCMeta):
    @staticmethod
    def send_chat_message(self, msg):
        """Định nghĩa phương thức gửi tin nhắn chat."""

# Lớp Client thực tế
class Client(IClient):
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        self.nickname = input("Choose a nickname: ")
        self.chat_history = deque(maxlen=25)
        self.chat_lock = threading.Lock()

    def send_chat_message(self, msg):
        """Gửi một tin nhắn chat đến server."""
        try:
            if msg:
                self.client.send(msg.encode(FORMAT))
        except socket.error as e:
            print(f"Socket error while sending: {e}")
            self.client.close()

    def receive_messages(self):
        """Vòng lặp để nhận tin nhắn từ server."""
        while True:
            try:
                message = self.client.recv(1024).decode(FORMAT)
                if message == 'NICK':
                    self.client.send(self.nickname.encode(FORMAT))
                elif message:
                    with self.chat_lock:
                        self.chat_history.append(message)
                else:
                    break
            except (ConnectionResetError, ConnectionAbortedError, OSError):
                print("Disconnected from the server.")
                break
        self.client.close()

    def run(self):
        """Khởi chạy các hoạt động của client."""
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        controller = ChessController.ChessController(self)
        controller.start("english", False)

# Lớp ProxyClient
class ProxyClient(IClient):
    def __init__(self):
        # --- THAY ĐỔI: Tạo đường dẫn tệp chính xác ---
        self.log_file_path = os.path.join(os.path.dirname(__file__), 'client_chat.txt')
        self.real_client = Client()
        try:
            with open(self.log_file_path, "w") as file:
                file.truncate(0)
        except IOError:
            print("Could not clear chat log file.")

    @property
    def chat_lock(self):
        return self.real_client.chat_lock

    @property
    def chat_history(self):
        return self.real_client.chat_history

    def send_chat_message(self, msg):
        """Gửi tin nhắn chat và ghi log."""
        try:
            # --- THAY ĐỔI: Sử dụng đường dẫn đã tạo ---
            with open(self.log_file_path, "a") as f:
                log_message = f'{self.real_client.nickname}: {msg}'
                f.write(log_message + " %s \n" % (datetime.datetime.now()))
        except IOError as e:
            print(f"Could not write to log file: {e}")
        self.real_client.send_chat_message(msg)

    def run(self):
        """Khởi chạy proxy client."""
        receive_thread = threading.Thread(target=self.real_client.receive_messages, daemon=True)
        receive_thread.start()
        controller = ChessController.ChessController(self)
        controller.start("english", False)

if __name__ == "__main__":
    p.init()
    newClient = ProxyClient()
    newClient.run()