from random import random

SCREENWIDTH = 288


class Generator:
    def get_width_left_and_beetween(self, level):
        beetween = 100
        left = SCREENWIDTH - beetween - 50
        return left, beetween
