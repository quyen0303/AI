import pygame as p
import os
from core import ChessController


def main(language, subscribed):

    controller = ChessController.ChessController()
    play_sound = p.mixer.Sound(r"images//menucut.mp3")
    play_sound.play()
    controller.playGame(language, subscribed)

if __name__ == "__main__":
    main("english", False)