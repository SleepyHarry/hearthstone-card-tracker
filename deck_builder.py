import pygame as pg
import os, sys, time, random, math
from useful import load_image, colors

from hsd_util import Deck
from deck_display import DeckDisplay

pg.init()

size = width, height = 1280, 960
fps_tgt = 30
clock = pg.time.Clock()

bgblue = (27, 30, 37)

screen = pg.display.set_mode(size)

dd = DeckDisplay(Deck.from_hsd("resource/decks/first.hsd"))

def done():
    pg.quit()
    sys.exit()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done()

        if event.type == pg.MOUSEBUTTONDOWN:
            m1, m3, m2 = pg.mouse.get_pressed()
            mX, mY = pg.mouse.get_pos()

        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()

            if keys[pg.K_ESCAPE]:
                done()

    screen.fill(bgblue)

    screen.blit(dd, (50, 65))
    
    pg.display.flip()

    clock.tick(fps_tgt)
