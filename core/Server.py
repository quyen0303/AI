# Import các thư viện cần thiết.
import socket
import threading

# --- Cấu hình các hằng số cho Server ---
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050
ADDR = (HOST, PORT)
FORMAT = 'utf-8'

# --- Khởi tạo Server ---
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# --- Quản lý Client ---
clients = []
nicknames = []

def broadcast(message):
    """Gửi một tin nhắn đến tất cả các client đang kết nối."""
    for client in clients:
        client.send(message)

def handle_client(conn, addr):
    """Xử lý kết nối cho từng client trong một luồng riêng."""
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True

    try:
        conn.send('NICK'.encode(FORMAT))
        nickname = conn.recv(1024).decode(FORMAT)
        nicknames.append(nickname)
        clients.append(conn)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} has joined the chat!".encode(FORMAT))

        while connected:
            try:
                message = conn.recv(1024)
                if message:
                    formatted_message = f"[{nickname}] {message.decode(FORMAT)}".encode(FORMAT)
                    print(f"Broadcasting: {formatted_message.decode(FORMAT)}")
                    broadcast(formatted_message)
                else:
                    raise ConnectionResetError
            except (ConnectionResetError, ConnectionAbortedError):
                if conn in clients:
                    index = clients.index(conn)
                    clients.remove(conn)
                    conn.close()
                    nickname = nicknames.pop(index)
                    broadcast(f'{nickname} has left the chat!'.encode(FORMAT))
                    print(f"[DISCONNECTED] {addr} ({nickname}) disconnected.")
                connected = False
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
        if conn in clients:
            clients.remove(conn)
        conn.close()

def start():
    """Khởi động server và lắng nghe kết nối mới."""
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}")
    while True:
        try:
            conn, addr = server.accept()
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