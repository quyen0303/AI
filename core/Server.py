# Import các thư viện cần thiết.
import socket  # Thư viện cho việc lập trình mạng (tạo client-server).
import threading  # Thư viện để xử lý nhiều client cùng lúc trên các luồng riêng biệt.

# --- Cấu hình các hằng số cho Server ---
# Lấy địa chỉ IP nội bộ của máy đang chạy server một cách tự động.
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050  # Cổng mạng mà server sẽ lắng nghe. Phải giống với cổng được cấu hình ở Client.
ADDR = (HOST, PORT)  # Tạo một tuple chứa địa chỉ IP và cổng.
FORMAT = 'utf-8'  # Định dạng mã hóa ký tự cho tin nhắn.
HEADER = 64  # Kích thước cố định của header (không được sử dụng trong phiên bản này, nhưng là một thực hành tốt).
DISCONNECT_MESSAGE = "!DISCONNECT" # Tin nhắn đặc biệt để ngắt kết nối (không được sử dụng trong phiên bản này).

# --- Khởi tạo Server ---
# Tạo một đối tượng socket mới sử dụng địa chỉ IPv4 (AF_INET) và giao thức TCP (SOCK_STREAM).
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Gán (bind) socket với địa chỉ IP và cổng đã cấu hình.
server.bind(ADDR)

# --- Quản lý Client ---
# Danh sách để lưu các đối tượng kết nối (socket) của client.
clients = []
# Danh sách để lưu nickname tương ứng với mỗi client.
nicknames = []


# Hàm gửi một tin nhắn đến tất cả các client đang kết nối.
def broadcast(message):
    """
    Gửi một tin nhắn đến tất cả các client đang kết nối.
    """
    # Lặp qua danh sách tất cả các đối tượng kết nối của client.
    for client in clients:
        # Gửi tin nhắn đến từng client.
        client.send(message)


# Hàm xử lý kết nối cho một client cụ thể. Mỗi client sẽ được chạy trên một luồng riêng.
def handle_client(conn, addr):
    """
    Xử lý kết nối cho từng client trong một luồng riêng.
    """
    print(f"[NEW CONNECTION] {addr} connected.") # In thông báo có kết nối mới ra console của server.
    connected = True # Biến cờ để kiểm soát vòng lặp.

    try:
        # Gửi yêu cầu 'Nickname:' đến client vừa kết nối.
        conn.send('Nickname:'.encode('ascii'))
        # Chờ và nhận nickname từ client (tối đa 1024 bytes).
        nickname = conn.recv(1024).decode('ascii')
        # Thêm nickname và đối tượng kết nối vào các danh sách tương ứng.
        nicknames.append(nickname)
        clients.append(conn)

        print(f"Nickname of the client is {nickname}") # In nickname của client ra console server.
        # Gửi thông báo cho tất cả các client khác rằng có người mới tham gia.
        broadcast(f"{nickname} has joined the chat!\n".encode('ascii'))
        # Gửi tin nhắn chào mừng đến client vừa kết nối.
        conn.send('Connected to the server!'.encode('ascii'))

        # Bắt đầu vòng lặp để nhận tin nhắn từ client này.
        while connected:
            try:
                # Chờ và nhận tin nhắn từ client.
                message = conn.recv(1024)
                if message: # Nếu nhận được tin nhắn (không phải là chuỗi rỗng).
                    # In tin nhắn ra console của server kèm theo nickname người gửi.
                    print(f"[{nickname}] {message.decode(FORMAT)}")
                    # Gửi tin nhắn đó đến tất cả các client khác.
                    broadcast(message)
                else:
                    # Nếu không nhận được tin nhắn (client đã đóng kết nối), ném ra lỗi.
                    raise ConnectionResetError
            # Xử lý khi client ngắt kết nối (ví dụ: đóng cửa sổ).
            except (ConnectionResetError, ConnectionAbortedError):
                # Kiểm tra xem client có còn trong danh sách không (để tránh lỗi).
                if conn in clients:
                    index = clients.index(conn) # Tìm vị trí của client trong danh sách.
                    clients.remove(conn) # Xóa client khỏi danh sách.
                    conn.close() # Đóng kết nối với client.
                    nickname = nicknames.pop(index) # Xóa nickname tương ứng.
                    # Thông báo cho các client còn lại rằng người này đã rời đi.
                    broadcast(f'{nickname} has left the chat!'.encode('ascii'))
                    print(f"[DISCONNECTED] {addr} ({nickname}) disconnected.")
                connected = False # Dừng vòng lặp cho client này.
    # Bắt các lỗi không mong muốn khác.
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
        # Dọn dẹp client nếu có lỗi.
        if conn in clients:
            clients.remove(conn)
        conn.close()


# Hàm chính để khởi động server và bắt đầu lắng nghe kết nối.
def start():
    """
    Khởi động server và lắng nghe kết nối mới.
    """
    server.listen() # Bắt đầu lắng nghe các kết nối đến.
    print(f"[LISTENING] Server is listening on {HOST}") # Thông báo server đã sẵn sàng.
    while True: # Vòng lặp vô hạn để server luôn chạy.
        try:
            # Chấp nhận một kết nối mới. Hàm này sẽ dừng cho đến khi có client kết nối.
            # `conn` là đối tượng socket mới cho client, `addr` là địa chỉ của client.
            conn, addr = server.accept()
            # Tạo một luồng (thread) mới để xử lý client này, để server có thể tiếp tục lắng nghe các kết nối khác.
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start() # Bắt đầu luồng.
            # In ra số lượng kết nối đang hoạt động (trừ đi luồng chính).
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        # Xử lý khi người dùng nhấn Ctrl+C để dừng server.
        except KeyboardInterrupt:
            print("\n[STOPPING] Server is shutting down.")
            # Đóng tất cả các kết nối client.
            for client in clients:
                client.close()
            server.close() # Đóng socket của server.
            break # Thoát khỏi vòng lặp chính.


# Đây là điểm bắt đầu thực thi khi bạn chạy tệp `Server.py`.
if __name__ == "__main__":
    print("[STARTING] Server is starting...") # In thông báo bắt đầu.
    start() # Gọi hàm start để khởi động server.