import socket
import threading

# Cấu hình Server
# Lấy địa chỉ IP cục bộ của máy. Phải giống với cấu hình trong Client.py
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050  # Phải cùng port với Client.py
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MESSAGE = "!DISCONNECT"

# Khởi tạo server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Danh sách để lưu các client đã kết nối và nickname của họ
clients = []
nicknames = []


def broadcast(message):
    """
    Gửi một tin nhắn đến tất cả các client đang kết nối.
    """
    for client in clients:
        client.send(message)


def handle_client(conn, addr):
    """
    Xử lý kết nối cho từng client trong một luồng riêng.
    """
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    # Yêu cầu và nhận nickname từ client
    try:
        conn.send('Nickname:'.encode('ascii'))
        nickname = conn.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(conn)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} has joined the chat!\n".encode('ascii'))
        conn.send('Connected to the server!'.encode('ascii'))

        while connected:
            try:
                # Nhận tin nhắn từ client
                message = conn.recv(1024)
                if message:
                    # Gửi tin nhắn nhận được đến tất cả client khác
                    print(f"[{nickname}] {message.decode(FORMAT)}")
                    broadcast(message)
                else:
                    # Nếu không nhận được tin nhắn, client đã ngắt kết nối
                    raise ConnectionResetError
            except (ConnectionResetError, ConnectionAbortedError):
                # Xử lý khi client ngắt kết nối
                if conn in clients:
                    index = clients.index(conn)
                    clients.remove(conn)
                    conn.close()
                    nickname = nicknames.pop(index)
                    broadcast(f'{nickname} has left the chat!'.encode('ascii'))
                    print(f"[DISCONNECTED] {addr} ({nickname}) disconnected.")
                connected = False
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
        if conn in clients:
            clients.remove(conn)
        conn.close()


def start():
    """
    Khởi động server và lắng nghe kết nối mới.
    """
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}")
    while True:
        try:
            # Chấp nhận kết nối mới
            conn, addr = server.accept()
            # Tạo một luồng mới để xử lý client vừa kết nối
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        except KeyboardInterrupt:
            print("\n[STOPPING] Server is shutting down.")
            for client in clients:
                client.close()
            server.close()
            break


if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start()

