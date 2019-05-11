import pygame

pygame.init()

SCREENWIDTH = 288
SCREENHEIGHT = 512

GRAVITY = 0.5


class Pipe:
    def __init__(self, left, right, square):
        self.square = square
        self.left_pipe_width = left
        self.right_pipe_width = right
        self.height = 10
        self.y = -self.height
        self.y_value = 0
        self.YVALUE = -10
        self.jump_delay = 0

        self.left_pressed = False
        self.right_pressed = False

    def update(self):
        self.y_value += GRAVITY

        if self.jump_delay > 0:
            self.jump_delay -= 1

        if self.left_pressed:
            self.y_value = self.YVALUE
            self.jump_delay = 5
            self.left_pressed = False
        elif self.right_pressed:
            self.y_value = self.YVALUE
            self.jump_delay = 5
            self.right_pressed = False

        if self.y_value < 0 and self.square.y <= SCREENHEIGHT / 2 - self.height / 2:
            self.y -= self.y_value

    def update_square(self):
        if self.y_value < 0 and self.square.y <= SCREENHEIGHT / 2 - self.height / 2:
            self.square.total_y -= self.y_value

    def synchronize_with_other_pipes(self, y_value, delay):
        self.y_value = y_value
        self.jump_delay = delay

    def collides(self, x, y, width, height):
        if y + height >= self.y and y <= self.y + self.height:
            return x <= self.left_pipe_width or x + width >= SCREENWIDTH - self.right_pipe_width
        return False
