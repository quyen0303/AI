# Import các thư viện cần thiết.
import socket  # Thư viện để tạo và quản lý kết nối mạng (sockets).
import threading  # Thư viện để chạy nhiều tác vụ đồng thời (mỗi client một luồng).

# --- Cấu hình các hằng số cho Server ---
# Lấy địa chỉ IP nội bộ của máy đang chạy server.
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050  # Chọn một cổng để server lắng nghe, ví dụ 5050.
ADDR = (HOST, PORT)  # Tạo một tuple chứa địa chỉ IP và cổng.
FORMAT = 'utf-8'  # Định dạng mã hóa để gửi và nhận tin nhắn.

# --- Khởi tạo Server ---
# Tạo một đối tượng socket, AF_INET chỉ định dùng giao thức IPv4, SOCK_STREAM chỉ định dùng TCP.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Gán địa chỉ và cổng đã định nghĩa cho socket của server.
server.bind(ADDR)

# --- Quản lý Client ---
# Danh sách để lưu trữ các đối tượng kết nối (socket) của tất cả client.
clients = []
# Danh sách để lưu trữ biệt danh (nickname) của tất cả client, tương ứng với danh sách clients.
nicknames = []


def broadcast(message):
    """Gửi một tin nhắn đến tất cả các client đang kết nối."""
    # Lặp qua từng đối tượng client trong danh sách.
    for client in clients:
        # Gửi tin nhắn đến client đó.
        client.send(message)


def handle_client(conn, addr):
    """
    Hàm này xử lý kết nối cho từng client. Mỗi client sẽ được chạy trong một luồng (thread) riêng.
    'conn' là đối tượng socket của client, 'addr' là địa chỉ của client.
    """
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    try:
        # 1. Yêu cầu và nhận nickname từ client.
        conn.send('NICK'.encode(FORMAT))  # Gửi yêu cầu 'NICK' đến client.
        nickname = conn.recv(1024).decode(FORMAT)  # Nhận nickname client gửi về.
        nicknames.append(nickname)  # Thêm nickname vào danh sách.
        clients.append(conn)      # Thêm kết nối của client vào danh sách.

        print(f"Nickname of the client is {nickname}")
        # Thông báo cho tất cả mọi người rằng có người mới tham gia.
        broadcast(f"{nickname} has joined the chat!".encode(FORMAT))

        # 2. Vòng lặp nhận tin nhắn từ client.
        while connected:
            try:
                message = conn.recv(1024)  # Chờ và nhận tin nhắn từ client.
                if message:
                    # Định dạng lại tin nhắn để có dạng "[nickname] message" và gửi cho mọi người.
                    formatted_message = f"[{nickname}] {message.decode(FORMAT)}".encode(FORMAT)
                    print(f"Broadcasting: {formatted_message.decode(FORMAT)}")
                    broadcast(formatted_message)
                else:
                    # Nếu không nhận được tin nhắn, coi như client đã ngắt kết nối.
                    raise ConnectionResetError
            except (ConnectionResetError, ConnectionAbortedError):
                # 3. Xử lý khi client ngắt kết nối.
                if conn in clients:
                    index = clients.index(conn)  # Tìm vị trí của client trong danh sách.
                    clients.remove(conn)        # Xóa kết nối.
                    conn.close()                 # Đóng kết nối.
                    nickname = nicknames.pop(index)  # Xóa nickname tương ứng.
                    # Thông báo cho mọi người rằng client này đã rời đi.
                    broadcast(f'{nickname} has left the chat!'.encode(FORMAT))
                    print(f"[DISCONNECTED] {addr} ({nickname}) disconnected.")
                connected = False # Kết thúc vòng lặp.
    except Exception as e:
        # Bắt các lỗi không mong muốn khác.
        print(f"Error handling client {addr}: {e}")
        if conn in clients:
            clients.remove(conn)
        conn.close()


def start():
    """Khởi động server và bắt đầu lắng nghe kết nối mới."""
    server.listen()  # Bắt đầu lắng nghe.
    print(f"[LISTENING] Server is listening on {HOST}")
    while True:
        try:
            # Chấp nhận một kết nối mới khi có client kết nối đến.
            # 'conn' là đối tượng socket của client, 'addr' là địa chỉ của họ.
            conn, addr = server.accept()
            # Tạo một luồng mới để xử lý client này, để server có thể tiếp tục lắng nghe các client khác.
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start() # Bắt đầu luồng.
            # In ra số lượng kết nối đang hoạt động.
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            # Xử lý khi người dùng nhấn Ctrl+C để tắt server.
            print("\n[STOPPING] Server is shutting down.")
            for client in clients:
                client.close() # Đóng tất cả các kết nối client.
            server.close() # Đóng server.
            break


# Đoạn mã này chỉ chạy khi file Server.py được thực thi trực tiếp.
if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start() # Gọi hàm start để bắt đầu server.