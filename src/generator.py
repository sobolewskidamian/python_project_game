from random import random
import main


class Generator:
    def get_width_left_and_beetween(self, level):
        beetween = 100
        left = main.SCREENWIDTH - beetween - 50
        return left, beetween
