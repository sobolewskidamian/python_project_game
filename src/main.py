import sys
import pygame
from pygame.locals import *

from objects.inputBox import InputBox
from objects.submitBox import SubmitBox
from game import Game

FPS = 70
SCREENWIDTH = 288
SCREENHEIGHT = 512

#to do
# ranking
# synchronizacja multiplayer
# gameover

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
                game.server_address, game.port = '192.168.43.92', 4321#get_multiplayer_data()  #'192.168.43.92', 4321
                game.multiplayer = True
            else:
                game.multiplayer = False
        game.play()


def choose_mode():
    submit_box = SubmitBox(SCREENWIDTH / 2 - 75, SCREENHEIGHT / 2 - 66, 150, 32, "Singleplayer")
    submit_box2 = SubmitBox(SCREENWIDTH / 2 - 75, SCREENHEIGHT / 2 - 6, 150, 32, "Multiplayer")

    boxes = [submit_box, submit_box2]
    while not submit_box.get_active() and not submit_box2.get_active():
        clean_screen()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            for box in boxes:
                box.handle_event(event)

        for box in boxes:
            box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    if submit_box2.get_active():
        return True
    else:
        return False


def get_multiplayer_data():
    input_box = InputBox(10, SCREENHEIGHT / 2 - 88, SCREENWIDTH - 20, 32)
    input_box2 = InputBox(10, SCREENHEIGHT / 2 - 8, SCREENWIDTH - 20, 32)
    submit_box = SubmitBox(SCREENWIDTH / 2 - 28, SCREENHEIGHT / 2 + 50, 56, 32, "Play")

    boxes = [input_box, input_box2, submit_box]
    while not submit_box.get_active() or input_box.get_text() == '' or input_box2.get_text() == '':
        clean_screen()
        SCREEN.blit(pygame.font.Font(None, 32).render('Server address:', True, pygame.Color('lightskyblue3')),
                    (10, SCREENHEIGHT / 2 - 120))
        SCREEN.blit(pygame.font.Font(None, 32).render('Server port:', True, pygame.Color('lightskyblue3')),
                    (10, SCREENHEIGHT / 2 - 40))

        submit_box.set_not_active()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == pygame.K_TAB and input_box.get_active():
                    input_box.set_not_active()
                    input_box2.set_active()
                elif event.key == pygame.K_TAB and input_box2.get_active():
                    input_box2.set_not_active()
                    input_box.set_active()
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    submit_box.set_active()
            for box in boxes:
                box.handle_event(event)

        for box in boxes:
            box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    try:
        port = int(input_box2.get_text())
    except Exception:
        port = 0
    return input_box.get_text(), port


def clean_screen():
    SCREEN.fill((248, 248, 255))


def get_nick():
    input_box = InputBox(10, SCREENHEIGHT / 2 - 16, SCREENWIDTH - 20, 32)
    submit_box = SubmitBox(SCREENWIDTH / 2 - 28, SCREENHEIGHT / 2 + 16 + 20, 56, 32, "Play")

    boxes = [input_box, submit_box]
    while not submit_box.get_active() or input_box.get_text() == '':
        SCREEN.fill((248, 248, 255))
        SCREEN.blit(pygame.font.Font(None, 32).render('Your nick:', True, pygame.Color('lightskyblue3')),
                    (SCREENWIDTH / 2 - 54, SCREENHEIGHT / 2 - 32 - 20))
        submit_box.set_not_active()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_RETURN or event.key == K_KP_ENTER):
                submit_box.set_active()
            for box in boxes:
                box.handle_event(event)

        for box in boxes:
            box.draw(SCREEN)

        pygame.display.flip()
        FPSCLOCK.tick(FPS)
    return input_box.get_text()


if __name__ == '__main__':
    main()
