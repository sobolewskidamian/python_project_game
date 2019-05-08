from random import random
import main


class Generator:
    def get_width_beetween_two_pipes(self, level):
        return 100

    def get_width_left(self, width_beetween_two_pipes):
        return main.SCREENWIDTH - width_beetween_two_pipes - 50
