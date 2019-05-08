from random import random

SCREENWIDTH = 288


class Generator:
    def get_width_left_and_beetween(self, level):
        beetween = random() * 200 / level + 100
        left = random() * (SCREENWIDTH - beetween)
        right = SCREENWIDTH - left - beetween
        return left, right
