import os, sys, time, random, math, string
import pygame as pg

from ctypes import windll

from useful import load_image, colors
from textFuncs import *

from hscheck import HSLog
from hsd_util import Deck
from deck_display import DeckDisplay, Card, cards

## Pygame display stuff
pg.init()

CARD_HEIGHT = 42
size = width, height = 245, CARD_HEIGHT*20
fps_tgt = 30
clock = pg.time.Clock()

screen = pg.display.set_mode(size, pg.NOFRAME)

#magic
windll.user32.SetWindowPos(pg.display.get_wm_info()["window"],
                           -1, 1920-width, 0, 0, 0, 0x0001)
##

log = HSLog()

bgblue = (27, 30, 37)

dd = DeckDisplay(Deck.from_hsd("resource/decks/first.hsd"))

def done():
    log.close_all()
    
    pg.quit()
    sys.exit()


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done()

        if event.type == pg.MOUSEBUTTONDOWN:
            m1, m3, m2 = pg.mouse.get_pressed()
            mX, mY = pg.mouse.get_pos()

            if m1:
                minions = cards["Minion"].keys()
                spells = cards["Ability"].keys()
                weapons = cards["Weapon"].keys()

                dd.add_card(random.choice(minions + spells + weapons))

            if m2:
                dd.take_card(random.choice(dd.deck["cards"].keys()))

        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()

            if keys[pg.K_ESCAPE]:
                done()

    screen.fill(bgblue)

    screen.blit(dd, (0, 0))
    
    pg.display.flip()

    clock.tick(fps_tgt)
