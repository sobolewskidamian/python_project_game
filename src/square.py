SCREENWIDTH = 288
SCREENHEIGHT = 512

GRAVITY = 0.5


class Square:
    def __init__(self, pid):
        self.pid = pid
        self.nick = ''
        self.hp = 100
        self.score = 0
        self.width = 20
        self.height = self.width
        self.x = SCREENWIDTH / 2 - self.width / 2
        self.y = SCREENHEIGHT / 2 - self.height / 2
        self.total_y = 0
        self.XVALUE = 3
        self.YVALUE = -10
        self.x_value = 0
        self.y_value = 0
        self.jump_delay = 0
        self.dead = False

        self.left_pressed = False
        self.right_pressed = False
        self.escape_pressed = False

    def update(self):
        self.y_value += GRAVITY

        if self.jump_delay > 0:
            self.jump_delay -= 1

        if self.escape_pressed:
            self.dead = True
            self.escape_pressed = False

        if not self.dead and self.jump_delay <= 0 and (self.left_pressed or self.right_pressed):
            self.y_value = self.YVALUE
            self.jump_delay = 5
            if self.left_pressed:
                self.x_value = -self.XVALUE
                self.left_pressed = False
            if self.right_pressed:
                self.x_value = self.XVALUE
                self.right_pressed = False

        if self.y_value > 0 or self.y > SCREENHEIGHT / 2 - self.height / 2:
            self.y += self.y_value

        self.x += self.x_value

        if self.x >= SCREENWIDTH:
            self.x = -self.width + 1
        elif self.x <= -self.width:
            self.x = SCREENWIDTH - 1
