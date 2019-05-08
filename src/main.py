import sys
import pygame
from pygame.locals import *

from objects.inputBox import InputBox
from objects.submitBox import SubmitBox

from game import Game

FPS = 70
SCREENWIDTH = 288
SCREENHEIGHT = 512


def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    SCREEN = pygame.display.set_mode([SCREENWIDTH, SCREENHEIGHT],0,32)
    pygame.display.set_caption('Vertical game')

    # nick = get_nick()
    while True:
        game = Game(SCREEN, FPSCLOCK, FPS)
        game.play()


def clean_screen():
    SCREEN.fill((248, 248, 255))
    pygame.display.update()


def get_nick():
    clean_screen()
    SCREEN.blit(pygame.font.Font(None, 32).render('Your nick:', True, pygame.Color('lightskyblue3')),
                (SCREENWIDTH / 2 - 54, SCREENHEIGHT / 2 - 32 - 20))
    input_box = InputBox(10, SCREENHEIGHT / 2 - 16, SCREENWIDTH - 20, 32)
    submit_box = SubmitBox(SCREENWIDTH / 2 - 28, SCREENHEIGHT / 2 + 16 + 20, 56, 32, "Play")

    while not submit_box.get_active() or input_box.get_text() == '':
        submit_box.set_not_active()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            input_box.handle_event(event)
            submit_box.handle_event(event)

        input_box.draw(SCREEN)
        submit_box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    return input_box.get_text()


if __name__ == '__main__':
    main()
