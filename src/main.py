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
    SCREEN = pygame.display.set_mode([SCREENWIDTH, SCREENHEIGHT], 0, 32)
    pygame.display.set_caption('Vertical game')

    nick = get_nick()
    # nick = 'damian'
    game = Game(nick, SCREEN, FPSCLOCK, FPS)
    while True:
        if game.game_ended:
            game.game_ended = False
            mode = choose_mode()
            if mode:
                game.server_address, game.port = get_multiplayer_data()  # '192.168.1.102', 4320  #
                game.multiplayer = True
            else:
                game.multiplayer = False
        game.play()


def choose_mode():
    clean_screen()
    submit_box = SubmitBox(SCREENWIDTH / 2 - 75, SCREENHEIGHT / 2 - 66, 150, 32, "Singleplayer")
    submit_box2 = SubmitBox(SCREENWIDTH / 2 - 75, SCREENHEIGHT / 2 - 6, 150, 32, "Multiplayer")

    while not submit_box.get_active() and not submit_box2.get_active():
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            submit_box.handle_event(event)
            submit_box2.handle_event(event)

        submit_box.draw(SCREEN)
        submit_box2.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    if submit_box2.get_active():
        return True
    else:
        return False


def get_multiplayer_data():
    clean_screen()
    SCREEN.blit(pygame.font.Font(None, 32).render('Server address:', True, pygame.Color('lightskyblue3')),
                (10, SCREENHEIGHT / 2 - 120))
    input_box = InputBox(10, SCREENHEIGHT / 2 - 88, SCREENWIDTH - 20, 32)
    SCREEN.blit(pygame.font.Font(None, 32).render('Server port:', True, pygame.Color('lightskyblue3')),
                (10, SCREENHEIGHT / 2 - 40))
    input_box2 = InputBox(10, SCREENHEIGHT / 2 - 8, SCREENWIDTH - 20, 32)
    submit_box = SubmitBox(SCREENWIDTH / 2 - 28, SCREENHEIGHT / 2 + 50, 56, 32, "Play")

    while not submit_box.get_active() or input_box.get_text() == '' or input_box2.get_text() == '':
        submit_box.set_not_active()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            input_box.handle_event(event)
            input_box2.handle_event(event)
            submit_box.handle_event(event)

        input_box.draw(SCREEN)
        input_box2.draw(SCREEN)
        submit_box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    return input_box.get_text(), int(input_box2.get_text())


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
