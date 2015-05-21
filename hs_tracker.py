import pygame as pg
import os, sys

from ctypes import windll
import Tkinter, tkFileDialog

from useful import colors
from textFuncs import *

from hscheck import HSLog
from hsd_util import Deck, CardNotInDeckError
from deck_display import DeckDisplay, ObservableDeck

sys.stderr = open("error.log", 'w')
_error = False

## Pygame display stuff
pg.init()

root = Tkinter.Tk()
root.withdraw()

CARD_HEIGHT = 42
size = width, height = 245, int(CARD_HEIGHT*24.5)
fps_tgt = 30
clock = pg.time.Clock()

screen = pg.display.set_mode(size, pg.NOFRAME)

#magic
windll.user32.SetWindowPos(pg.display.get_wm_info()["window"],
                           -1, 1920-width, 0, 0, 0, 0x0001)
##

log = HSLog()

bgblue = (27, 30, 37)

screen.fill(bgblue)
pg.display.flip()

#TODO: ObservableDeck changes

if len(sys.argv) > 1:
    #we've been given a filename
    file_path = sys.argv[1]
else:
    #TODO: abstract this into a function, as it's repeated further down
    file_path = tkFileDialog.askopenfilename(
        defaultextension="hsd",
        initialdir="resource/decks")

if file_path and os.path.splitext(file_path)[-1] == ".hsd":
    deck = ObservableDeck.from_hsd(file_path)
else:
    #we allow this, on the proviso that later on the user loads a .hsd by using
    #ctrl+O
    deck = ObservableDeck()

dd = DeckDisplay(deck)

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

        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()
            keymods = pg.key.get_mods()

            shift = bool(keymods & 3)
            ctrl = bool(keymods & 196)

            if keys[pg.K_ESCAPE]:
                done()

            if ctrl and event.key == pg.K_o:
                file_path = tkFileDialog.askopenfilename(
                    defaultextension="hsd",
                    initialdir="resource/decks")

                if file_path and os.path.splitext(file_path)[-1] == ".hsd":
                    deck.replace(ObservableDeck.from_hsd(file_path))

    #get live info
    result, drawn_dict = log.result, log.drawn

    if result:
        deck.reset()
    elif any(drawn_dict.values()):
        #TODO: Error handling (wrong deck etc.)
        for card in drawn_dict['d']:
            try:
                deck.take_card(card, remember=True)
            except CardNotInDeckError as e:
                #Burrowing Mine triggers this, so there are genuine
                #reasons for it to happen in normal play

                #Also, secrets trigger twice, which is a bug that should be
                #fixed in hsd_util.py
                print >> sys.stderr, "Card not in deck: ", e.message
                sys.stderr.flush()
                _error = True
        
        #mulligans
        for card in drawn_dict['m']:
            deck.add_card(card)

            #these cards have previously been drawn, so we need to make
            #sure that the deck doesn't remember them twice
            #TODO: make this look better, there's a reason it's got an _
            try:
                #This threw a ValueError once, but due to a lack of
                #descriptive errors, I have no idea what caused it.
                deck._reset_additions.remove(card)
            except ValueError as e:
                #TODO: use logging module
                print >> sys.stderr, e.message, card
                sys.stderr.flush()
                _error = True

    screen.fill(bgblue)

    screen.blit(dd, (0, 0))

    if _error:
        screen.fill(colors.red, (width/4, height-10, width/2, 10))
    
    pg.display.flip()

    clock.tick(fps_tgt)
