import pygame as p
import ChessController

def main(language, subscribed):

    controller = ChessController.ChessController()
    playSound = p.mixer.Sound("images/menucut.mp3")
    playSound.play()
    controller.playGame(language, subscribed)

if __name__ == "__main__":
    main("english", False)