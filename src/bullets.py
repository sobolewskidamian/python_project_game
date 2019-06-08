import pygame

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512

SPEED = 0.7
DAMAGE_PLAYER = 5
DAMAGE_BOSS = 10

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.y_change = 0

    def if_hit(self, x, y, width, height):
        if self.x + 3 > x and self.x < x + width \
                and y < self.y < y + height:
            return True
        return False


class Rocket:
    def __init__(self, x, y, altitude):
        self.x = x
        self.y = y
        self.altitude = altitude

    def if_got_shot(self, x, y, width, height):
        if self.x + 5 > x and self.x < x + width \
                and self.y + 9 > y and self.y < y + height:
            return True
        return False


class FireBallLeft:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def if_got_shot(self, x, y, width, height):
        if self.x + 7 > x and self.x < x + width \
                and self.y + 5 > y and self.y < y + height:
            return True
        return False


class FireBallRight:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def if_got_shot(self, x, y, width, height):
        if self.x + 7 > x and self.x < x + width \
                and self.y + 5 > y and self.y < y + height:
            return True
        return False


class BossBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.y_change = 0

    def if_got_shot(self, x, y, width, height):
        if self.x + 3 > x and self.x < x + width\
                and self.y + 4 > y and self.y < y + height:
            return True
        return False
