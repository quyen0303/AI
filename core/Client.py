import socket
import pygame as p
import threading
from abc import ABCMeta
import datetime
from core import ChessController

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)


class IClient(metaclass=ABCMeta):

    @staticmethod
    def send(self, msg):
        """ISendMethod"""

    @staticmethod
    def playChess(self, language, subscribed):
        """IPlayMethod"""

    @staticmethod
    def write(self):
        """IWriteMethod"""

    @staticmethod
    def receive(self):
        """IReceive"""

    @staticmethod
    def run(self):
        """IReceive"""


class Client(IClient):

    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(ADDR)
        self.nickname = input("Choose a nickname: ")

    def send(self, msg):
        message = msg.encode(FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode(FORMAT))

    def playChess(self, language, subscribed):
        # Phương thức này sẽ chạy game trong một luồng riêng
        controller = ChessController.ChessController()
        controller.start(language, subscribed)

    def write(self):
        # Chức năng này bị vô hiệu hóa vì hàm input() chặn hiển thị đồ họa game
        while False:  # Vòng lặp này sẽ không bao giờ chạy
            message = '{}: {}'.format(self.nickname, input(''))
            self.client.send(message.encode('ascii'))
            # write_thread = threading.Thread(target=self.write)
            # write_thread.start()

    def receive(self):
        while True:
            try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'Nickname:':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    print(message)
            except (ConnectionResetError, ConnectionAbortedError):
                print("An error occurred! Disconnecting...")
                self.client.close()
                break

    def run(self):
        # Luồng nhận tin nhắn vẫn hoạt động bình thường
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        # SỬA LỖI: Vô hiệu hóa luồng nhập chat (write_thread)
        # vì nó gây xung đột và chặn cửa sổ game hiển thị.
        # write_thread = threading.Thread(target=self.write)
        # write_thread.start()

        # Chạy game trong một luồng riêng
        chess_thread = threading.Thread(target=self.playChess, args=("english", False))
        chess_thread.start()


class ProxyClient(IClient):

    def __init__(self):
        self.Client = Client()
        try:
            with open(r"core/client_chat.txt", "w") as file:
                file.truncate(0)
        except IOError:
            print("Could not clear chat log file.")

    def send(self, msg):
        self.Client.send()

    def playChess(self, language, subscribed):
        try:
            with open(r"core/client_chat.txt", "a") as f:
                f.write("opened chess app proxy" + " %s \n" % (datetime.datetime.now()))
        except IOError as e:
            print(f"Could not write to log file: {e}")
        self.Client.playChess(language, subscribed)

    def write(self):
        # Vô hiệu hóa chức năng chat để không block game
        while False:
            message = '{}: {}'.format(self.Client.nickname, input(''))
            try:
                with open(r"core/client_chat.txt", "a") as f:
                    f.write(message + " %s \n" % (datetime.datetime.now()))
            except IOError as e:
                print(f"Could not write to log file: {e}")
            self.Client.client.send(message.encode('ascii'))

    def receive(self):
        self.Client.receive()

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        # SỬA LỖI: Vô hiệu hóa luồng nhập chat (write_thread)
        # write_thread = threading.Thread(target=self.write)
        # write_thread.start()

        chess_thread = threading.Thread(target=self.playChess, args=("english", False))
        chess_thread.start()


if __name__ == "__main__":
    p.init()  # Khởi tạo Pygame cho Client
    newClient = ProxyClient()
    newClient.run()

