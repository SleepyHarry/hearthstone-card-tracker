import pygame as pg
import os, sys, time, random, math

from useful import load_image, colors
from textFuncs import *

from hsd_util import Deck
from deck_display import DeckDisplay, all_cards, collectible_cards, get_card

pg.init()

size = width, height = 1280, 960
fps_tgt = 30
clock = pg.time.Clock()

bgblue = (27, 30, 37)

screen = pg.display.set_mode(size)

dd = DeckDisplay()
dd_rect = dd.get_rect(right=width-10, top=10)

#yellow outline
outline_rect = dd.get_rect(left=dd_rect.left-1, top=dd_rect.top-1,
                           width=dd_rect.width+2, height=dd_rect.height+2)

def card_suggestions(partial, collectible=True):
    """ Returns a list of all cards that partial could refer to.
        An autocomplete of sorts.
    """

    cards = all_cards if not collectible else collectible_cards

    return [name for t in cards.keys()
            for name, cardobj in cards[t].items()
            if partial.strip().lower() in name.lower()]

class Textbox(pg.Surface):
    """ A blittable object that can be given text to display. """

    def __init__(self, initial_text, size):
        super(Textbox, self).__init__(size, pg.SRCALPHA)

        self._text = initial_text

        self._update()

    def _update(self):
        self.fill((0, 0, 0, 0))

        #yellow underline
        w, h = self.get_size()
        self.fill(colors.yellow, (0, h-1, w, 1))
        
##        if self._text:
        text = textOutline(fontL, self._text + '_',
                           colors.white, colors.black)
        text_rect = text.get_rect(left=5, centery=self.get_size()[1]/2)

        self.blit(text, text_rect)

    def handle_keyboard_input(self, event):
        """ event should be a pg.KEYDOWN event """

        #this is super ugly - is there a better way? (TODO)

        keymods = pg.key.get_mods()
        shift = bool(keymods & 3)

        if event.key == 8:
            #backspace
            self._text = self._text[:-1]
        elif 96 < event.key <= 96+26:
            #letters
            self._text += chr(event.key - shift*32)
        elif 47 < event.key <= 47+10:
            #numbers
            if not shift:
                self._text += chr(event.key)
            else:
                if event.key == 49:
                    #exclamation mark
                    self._text += '!'
        elif event.key == 59:
            #semi-colon
            if shift:
                self._text += ':'
        elif event.key == 45:
            #hyphen
            self._text += '-'
        elif event.key == 44:
            #comma
            self._text += ','
        elif event.key == 46:
            #full-stop
            self._text += '.'
        elif event.key == 39:
            #apostrophe
            self._text += '\''
        elif event.key == 32:
            #space
            self._text += ' '
        elif event.key == 13:
            #enter
            if self._text:
                suggestions = card_suggestions(self._text)

                if suggestions:
                    self._text = ''
                    self._update()
                    return suggestions[0]
            else:
                dd.add_again()
##        else:
##            print event.key

        self._update()

        #TODO:
        #   Enter

tb = Textbox('', (3*width/4, height/16))
tb_rect = tb.get_rect(right=dd_rect.left - 20, centery=height/2)

selected_card = None

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

            selected_card = tb.handle_keyboard_input(event)

    if selected_card:
        dd.add_card(selected_card)
        selected_card = None

    suggestions = card_suggestions(tb._text) if tb._text else []

    screen.fill(bgblue)

    screen.fill(colors.yellow, outline_rect)
    screen.blit(dd, dd_rect)

    screen.blit(tb, tb_rect)

    for i, suggestion in enumerate(suggestions[:10]):
        text = textOutline(fontM, suggestion, colors.white, colors.black)
        screen.blit(text, text.get_rect(left=tb_rect.left+5,
                            top=tb_rect.bottom+(i*fontM.get_height())))
    
    pg.display.flip()

    clock.tick(fps_tgt)
