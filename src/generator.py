from random import random

SCREENWIDTH = 288


class Generator:
    @staticmethod
    def get_width_left_and_between(level):
        between = random() * 200 / (level + 1) + 100
        left = random() * (SCREENWIDTH - between)
        right = SCREENWIDTH - left - between
        return left, right
