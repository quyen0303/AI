# Import các thư viện cần thiết.
import socket  # Thư viện cho việc lập trình mạng (tạo client-server).
import pygame as p  # Thư viện để chạy game (cần khởi tạo dù game logic ở Controller).
import threading  # Thư viện để chạy nhiều công việc đồng thời (game và chat).
from abc import ABCMeta  # Dùng để tạo Lớp cơ sở trừu tượng (Abstract Base Class), một phần của thiết kế hướng đối tượng.
import datetime  # Dùng để lấy thời gian hiện tại cho việc ghi log.
from core import ChessController  # Import lớp Controller để có thể khởi chạy game.

# --- Cấu hình mạng cho Client ---
HEADER = 64  # Kích thước cố định của header, dùng để gửi độ dài của tin nhắn.
PORT = 5050  # Cổng kết nối, phải giống với cổng trên Server.
FORMAT = 'utf-8'  # Định dạng mã hóa ký tự cho tin nhắn.
DISCONNECT_MESSAGE = "!DISCONNECT"  # Tin nhắn đặc biệt để ngắt kết nối.
# Tự động lấy địa chỉ IP của máy chạy server (giả định client và server trên cùng mạng).
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)  # Tuple chứa địa chỉ IP và cổng của server.


# Lớp cơ sở trừu tượng (Interface) định nghĩa cấu trúc cho các lớp Client.
# Bất kỳ lớp nào kế thừa từ IClient đều nên có các phương thức này.
class IClient(metaclass=ABCMeta):

    @staticmethod
    def send(self, msg):
        """Định nghĩa phương thức gửi tin nhắn."""

    @staticmethod
    def playChess(self, language, subscribed):
        """Định nghĩa phương thức bắt đầu game cờ."""

    @staticmethod
    def write(self):
        """Định nghĩa phương thức để người dùng nhập và gửi tin nhắn."""

    @staticmethod
    def receive(self):
        """Định nghĩa phương thức nhận tin nhắn từ server."""

    @staticmethod
    def run(self):
        """Định nghĩa phương thức chính để chạy client."""


# Lớp Client thực tế, xử lý logic kết nối và giao tiếp.
class Client(IClient):

    # Hàm khởi tạo, được gọi khi một đối tượng Client được tạo.
    def __init__(self):
        # Tạo một đối tượng socket (TCP).
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Kết nối đến địa chỉ của server.
        self.client.connect(ADDR)
        # Yêu cầu người dùng nhập nickname từ giao diện dòng lệnh (console).
        self.nickname = input("Choose a nickname: ")

    # Phương thức gửi tin nhắn (chưa được sử dụng trong logic game).
    def send(self, msg):
        message = msg.encode(FORMAT) # Mã hóa tin nhắn sang bytes.
        msg_length = len(message) # Lấy độ dài của tin nhắn.
        send_length = str(msg_length).encode(FORMAT) # Chuyển độ dài thành chuỗi và mã hóa.
        # Đệm thêm khoảng trắng để header luôn có độ dài cố định (64 bytes).
        send_length += b' ' * (HEADER - len(send_length))
        self.client.send(send_length) # Gửi header chứa độ dài.
        self.client.send(message) # Gửi tin nhắn thực tế.
        print(self.client.recv(2048).decode(FORMAT)) # In ra phản hồi từ server.

    # Phương thức để bắt đầu game cờ vua.
    def playChess(self, language, subscribed):
        # Tạo một đối tượng Controller, Controller sẽ quản lý toàn bộ game.
        controller = ChessController.ChessController()
        # Bắt đầu vòng lặp của game (từ menu chính).
        controller.start(language, subscribed)

    # Phương thức để người dùng nhập và gửi tin nhắn chat.
    def write(self):
        # **QUAN TRỌNG**: Chức năng này đã bị vô hiệu hóa (`while False`).
        # Lý do: hàm `input()` sẽ dừng chương trình để chờ người dùng nhập,
        # điều này sẽ làm "đóng băng" cửa sổ đồ họa của game Pygame.
        while False:  # Vòng lặp này sẽ không bao giờ được thực thi.
            message = '{}: {}'.format(self.nickname, input(''))
            self.client.send(message.encode('ascii'))

    # Phương thức để liên tục lắng nghe và nhận tin nhắn từ server.
    def receive(self):
        while True: # Vòng lặp vô hạn để luôn sẵn sàng nhận tin.
            try:
                # Chờ và nhận dữ liệu từ server (tối đa 1024 bytes).
                message = self.client.recv(1024).decode('ascii')
                # Nếu server yêu cầu nickname, gửi nickname đã nhập.
                if message == 'Nickname:':
                    self.client.send(self.nickname.encode('ascii'))
                else:
                    # In bất kỳ tin nhắn nào khác ra console.
                    print(message)
            # Xử lý lỗi nếu server đột ngột ngắt kết nối.
            except (ConnectionResetError, ConnectionAbortedError):
                print("An error occurred! Disconnecting...")
                self.client.close() # Đóng kết nối.
                break # Thoát khỏi vòng lặp.

    # Phương thức chính để khởi chạy các hoạt động của client.
    def run(self):
        # Tạo một luồng mới để chạy hàm `receive` (để không chặn luồng chính).
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start() # Bắt đầu luồng nhận tin nhắn.

        # **SỬA LỖI**: Luồng `write` đã bị vô hiệu hóa để tránh xung đột với Pygame.
        # write_thread = threading.Thread(target=self.write)
        # write_thread.start()

        # Tạo một luồng mới để chạy game cờ vua.
        chess_thread = threading.Thread(target=self.playChess, args=("english", False))
        chess_thread.start() # Bắt đầu luồng game.


# Lớp ProxyClient, triển khai mẫu thiết kế Proxy.
# Lớp này "bọc" lớp Client thật để thêm chức năng (ghi log) mà không thay đổi code gốc của Client.
class ProxyClient(IClient):

    # Hàm khởi tạo của Proxy.
    def __init__(self):
        # Tạo một đối tượng của lớp Client thật và lưu lại.
        self.Client = Client()
        try:
            # Mở tệp log ở chế độ ghi ('w') để xóa nội dung cũ mỗi khi chạy.
            with open(r"core/client_chat.txt", "w") as file:
                file.truncate(0)
        except IOError:
            print("Could not clear chat log file.")

    # Phương thức `send` của Proxy chỉ đơn giản là gọi `send` của Client thật.
    def send(self, msg):
        self.Client.send(msg) # Ủy quyền (delegate) công việc cho đối tượng Client thật.

    # Phương thức `playChess` của Proxy được thêm chức năng ghi log.
    def playChess(self, language, subscribed):
        try:
            # Mở tệp log ở chế độ ghi nối tiếp ('a').
            with open(r"core/client_chat.txt", "a") as f:
                # Ghi lại sự kiện mở ứng dụng cờ vua cùng với thời gian.
                f.write("opened chess app proxy" + " %s \n" % (datetime.datetime.now()))
        except IOError as e:
            print(f"Could not write to log file: {e}")
        # Sau khi ghi log, gọi phương thức `playChess` của Client thật để chạy game.
        self.Client.playChess(language, subscribed)

    # Phương thức `write` của Proxy cũng bị vô hiệu hóa giống như Client thật.
    def write(self):
        while False:
            message = '{}: {}'.format(self.Client.nickname, input(''))
            try:
                # Nếu được kích hoạt, nó sẽ ghi tin nhắn ra log trước khi gửi.
                with open(r"core/client_chat.txt", "a") as f:
                    f.write(message + " %s \n" % (datetime.datetime.now()))
            except IOError as e:
                print(f"Could not write to log file: {e}")
            self.Client.client.send(message.encode('ascii'))

    # Phương thức `receive` của Proxy ủy quyền hoàn toàn cho Client thật.
    def receive(self):
        self.Client.receive()

    # Phương thức `run` của Proxy có cấu trúc giống hệt `run` của Client thật.
    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        # Luồng `write` cũng bị vô hiệu hóa ở đây.
        # write_thread = threading.Thread(target=self.write)
        # write_thread.start()

        # Chạy game thông qua phương thức `playChess` của Proxy (đã được thêm chức năng ghi log).
        chess_thread = threading.Thread(target=self.playChess, args=("english", False))
        chess_thread.start()


# Đây là điểm bắt đầu thực thi khi bạn chạy tệp `Client.py`.
if __name__ == "__main__":
    p.init()  # Khởi tạo Pygame cho toàn bộ ứng dụng Client.
    # Tạo một đối tượng ProxyClient. Điều này có nghĩa là mặc định, ứng dụng sẽ chạy với chức năng ghi log.
    newClient = ProxyClient()
    # Bắt đầu chạy client.
    newClient.run()