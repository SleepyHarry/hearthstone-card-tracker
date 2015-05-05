import pygame as pg
import os, sys, time, random, math

import Tkinter, tkFileDialog

from useful import load_image, colors
from textFuncs import *

from hsd_util import Deck
from deck_display import DeckDisplay, all_cards, collectible_cards, get_card

pg.init()

root = Tkinter.Tk()
root.withdraw()

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

class Textbox(pg.Surface):
    """ A blittable object that can be given text to display. """

    def __init__(self, initial_text, size, dd):
        super(Textbox, self).__init__(size, pg.SRCALPHA)

        self.dd = dd
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


    def handle_keyboard_input(self, key):
        """ event should be a pg.KEYDOWN event """

        #this is super ugly - is there a better way? (TODO)

        keymods = pg.key.get_mods()
        shift = bool(keymods & 3)
        ctrl = bool(keymods & 196)

        if ctrl:
            if 96 < key <= 96+26:
                k = chr(key)

                if k == 'z':
                    self.dd.take_last()
                elif k == 's':
                    #TODO: refocus main window
                    file_path = tkFileDialog.asksaveasfilename(
                        defaultextension="hsd",
                        initialdir="resource/decks")

                    if file_path and os.path.splitext(file_path)[-1] == ".hsd":
                        self.dd.save(file_path, True)
                    else:
                        #TODO: raise a meaningful error
                        pass
                elif k == 'o':
                    file_path = tkFileDialog.askopenfilename(
                        defaultextension="hsd",
                        initialdir="resource/decks")
                    if file_path and os.path.splitext(file_path)[-1] == ".hsd":
                        self.dd = DeckDisplay(Deck.from_hsd(file_path))
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

                        self.dd.add_card(suggs[0])
                else:
                    self.dd.add_again()
##            else:
##                print key

        self._update()

tb = Textbox('', (3*width/4, height/16), dd)
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

##    suggestions = card_suggestions(tb.text) if tb.text else []

    screen.fill(bgblue)

    screen.fill(colors.yellow, outline_rect)
    screen.blit(tb.dd, dd_rect)

    screen.blit(tb, tb_rect)

    for i, suggestion in enumerate(tb.suggestions[:10]):
        text = textOutline(fontM, suggestion, colors.white, colors.black)
        screen.blit(text, text.get_rect(left=tb_rect.left+5,
                            top=tb_rect.bottom+(i*fontM.get_height())))
    
    pg.display.flip()

    clock.tick(fps_tgt)
