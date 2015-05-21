import pygame as pg
import os, sys, time, random, math, re

import Tkinter, tkFileDialog

from useful import load_image, colors
from textFuncs import *

from hsd_util import Deck
from deck_display import DeckDisplay, ManaCurve, ObservableDeck,\
                         collectible_cards


pg.init()

root = Tkinter.Tk()
root.withdraw()

size = width, height = 1280, 960
fps_tgt = 30
clock = pg.time.Clock()

bgblue = (27, 30, 37)

screen = pg.display.set_mode(size)

class Textbox(pg.Surface):
    """ A blittable object that can be given text to display. """

    def __init__(self, initial_text, size, deck):
        super(Textbox, self).__init__(size, pg.SRCALPHA)

        self.deck = deck
        self.text = initial_text

        self.offset = 0

        self._update()

    def _update(self):
        self.fill((0, 0, 0, 0))

        #yellow underline
        w, h = self.get_size()
        self.fill(colors.yellow, (0, h-1, w, 1))
        
##        if self.text:
        text = textOutline(fontL, self.text + '_',
                           colors.white, colors.black)
        text_rect = text.get_rect(left=5, centery=self.get_size()[1]/2)

        self.blit(text, text_rect)

    @property
    def suggestions(self):
        """ Returns a list of all cards that partial could refer to.
            An autocomplete of sorts.
        """

        if not self.text:
            return []

        raw = [name for t in collectible_cards.keys()
               for name, cardobj in collectible_cards[t].items()
               if self.text.strip().lower() in name.lower()]

        self.offset = self.offset % len(raw) if raw else 0

        #offset allows cycling
        return raw[self.offset:] + raw[:self.offset]

    @staticmethod
    def filename_format(file_path):
        """ Replaces certain tokens in file_path with appropriate things """

        file_path = re.sub(r"(?<!%)%DATE%",
                           time.strftime("%Y-%m-%d", time.localtime()),
                           file_path)

        file_path = re.sub(r"(?<!%)%TIME%",
                           time.strftime("%H%M", time.localtime()),
                           file_path)

        #TODO: %HERO%

        file_path = file_path.replace("%%", '%')

        return file_path

    def handle_keyboard_input(self, key):
        """ event should be a pg.KEYDOWN event """

        #TODO: this is super ugly - is there a better way?

        keymods = pg.key.get_mods()
        shift = bool(keymods & 3)
        ctrl = bool(keymods & 196)

        if ctrl:
            if 96 < key <= 96+26:
                k = chr(key)

                if k == 'z':
                    self.deck.take_last()
                elif k == 'r':
                    self.deck.clear()
                elif k == 's':
                    #TODO: refocus main window
                    file_path = tkFileDialog.asksaveasfilename(
                        defaultextension="hsd",
                        initialdir="resource/decks")

                    file_path = self.filename_format(file_path)

                    if file_path and os.path.splitext(file_path)[-1] == ".hsd":
                        self.deck.save(file_path, True)
                    else:
                        #TODO: raise a meaningful error
                        pass
                elif k == 'o':
                    file_path = tkFileDialog.askopenfilename(
                        defaultextension="hsd",
                        initialdir="resource/decks")
                    if file_path and os.path.splitext(file_path)[-1] == ".hsd":
                        #swap decks in place so that observers are preserved
                        self.deck.clear()

                        new_deck = ObservableDeck.from_hsd(file_path)

                        #this is a dict.update
                        self.deck.update(new_deck)
                        self.deck.notify_observers()
        else:
            if key == pg.K_BACKSPACE:
                #backspace
                self.text = self.text[:-1]
            elif 96 < key <= 96+26:
                #letters
                self.text += chr(key - shift*32)
            elif 47 < key <= 47+10:
                #numbers
                if not shift:
                    self.text += chr(key)
                else:
                    if key == 49:
                        #exclamation mark
                        self.text += '!'
            elif key == pg.K_SEMICOLON:
                #semi-colon
                if shift:
                    self.text += ':'
            elif key == pg.K_MINUS:
                #hyphen
                self.text += '-'
            elif key == pg.K_COMMA:
                #comma
                self.text += ','
            elif key == pg.K_PERIOD:
                #full-stop
                self.text += '.'
            elif key == pg.K_QUOTE:
                #apostrophe
                self.text += '\''
            elif key == pg.K_SPACE:
                #space
                self.text += ' '
            elif key in (pg.K_UP, pg.K_DOWN, pg.K_LEFT, pg.K_RIGHT):
                #arrow key
                if key == pg.K_UP:
                    self.offset -= 1
                elif key == pg.K_DOWN:
                    self.offset += 1
            elif key == 13:
                #enter
                if self.text:
                    suggs = self.suggestions
                    if suggs:
                        self.text = ''
                        self._update()

                        self.deck.add_card(suggs[0])
                else:
                    self.deck.add_again()
##            else:
##                print key

        self._update()

deck = ObservableDeck()

dd = DeckDisplay(deck, height_in_cards=20)
dd_rect = dd.get_rect(right=width-10, top=10)

#yellow outline
outline_rect = dd.get_rect(left=dd_rect.left-1, top=dd_rect.top-1,
                           width=dd_rect.width+2, height=dd_rect.height+2)

mc = ManaCurve(deck)
mc_rect = mc.get_rect(centerx=width/2, top=100)

tb = Textbox('', (3*width/4, height/16), deck)
tb_rect = tb.get_rect(right=dd_rect.left - 20, centery=height/2)

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

            tb.handle_keyboard_input(event.key)

    screen.fill(bgblue)

    screen.fill(colors.yellow, outline_rect)
    screen.blit(dd, dd_rect)

    cards_in_deck_text = textOutline(fontM, "{}/30".format(len(deck)),
                                     colors.white, colors.black)
    screen.blit(cards_in_deck_text,
                cards_in_deck_text.get_rect(top=dd_rect.bottom + 10,
                                            right=dd_rect.right - 5))

    screen.blit(tb, tb_rect)

    screen.blit(mc, mc_rect)

    for i, suggestion in enumerate(tb.suggestions[:10]):
        text = textOutline(fontM, suggestion,
                           colors.white if i else colors.cyan,
                           colors.black)
        screen.blit(text, text.get_rect(left=tb_rect.left+5,
                            top=tb_rect.bottom+(i*fontM.get_height())))
    
    pg.display.flip()

    clock.tick(fps_tgt)
