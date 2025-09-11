import pygame as p
from core import ChessController


def main(language, subscribed):
    """
    Điểm khởi đầu chính của ứng dụng khi không chạy qua client-server.
    """
    # Khởi tạo controller, controller sẽ tự động xử lý vòng lặp ứng dụng.
    controller = ChessController.ChessController()

    # SỬA LỖI: Gọi phương thức start() thay vì playGame() đã bị xóa.
    # Phương thức start() giờ đây sẽ quản lý toàn bộ vòng lặp (menu -> game).
    controller.start(language, subscribed)


if __name__ == "__main__":
    # Khởi tạo pygame một lần duy nhất ở đây.
    p.init()
    main("english", False)