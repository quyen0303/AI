import socket
import ChessController
import pygame as p
import threading
from abc import ABCMeta
import datetime

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
        controller = ChessController.ChessController()
        playSound = p.mixer.Sound("images/menucut.mp3")
        playSound.play()
        controller.playGame(language, subscribed)

    def write(self):
        while True:
            message = '{}: {}'.format(self.nickname, input(''))
            self.client.send(message.encode('ascii'))

    def receive(self):
         while True:
             try:
                message = self.client.recv(1024).decode('ascii')
                if message == 'Nickname:':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                     print(message)
             except:
                     print("An error occured!")
                     self.client.close()
                     break

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

        chess_thread = threading.Thread(target=self.playChess("english", False))
        chess_thread.start()

class ProxyClient(IClient):

    def __init__(self):
        self.Client = Client()
        file = open("client_chat.txt", "r+")
        file.truncate(0)
        file.close()

    def send(self, msg):
        self.Client.send()

    def playChess(self, language, subscribed):
        f = open("client_chat.txt", "a")
        f.write("opened chess app proxy" + " %s \n" % (datetime.datetime.now()))
        f.close()
        self.Client.playChess(language, subscribed)

    def write(self):
        while True:
            message = '{}: {}'.format(self.Client.nickname, input(''))
            f = open("client_chat.txt", "a")
            f.write(message + " %s \n" % (datetime.datetime.now()))
            f.close()
            self.Client.client.send(message.encode('ascii'))

    def receive(self):
        self.Client.receive()

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

        chess_thread = threading.Thread(target=self.playChess("english", False))
        chess_thread.start()

newClient = ProxyClient()
newClient.run()
