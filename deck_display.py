import pygame as pg

import json

from useful import load_image, colors
from textFuncs import *

from hsd_util import Deck

CARD_HEIGHT = 42
size = width, height = 245, CARD_HEIGHT*20

bgblue = (27, 30, 37)

all_cards = json.load(open("resource/cards.json"))["cards"]

#This is not perfect. For example, "Misha" and "Devilsaur" are in here
collectible_cards = {t: {name: card for name, card in all_cards[t].items()
                         if card["rarity"] != u'0'}
                     for t in ["Minion", "Weapon", "Ability"]}


class NoSuchCard(KeyError):
    pass

class Card:
    def __init__(self, card_data):
        for k, v in card_data.items():
            setattr(self, k, v)

def get_card(cardname, collectible=True):
    cards = collectible_cards if collectible else all_cards

    for possible in cards.keys():
        try:
            return Card(cards[possible][cardname])
        except KeyError:
            pass

    raise NoSuchCard("Cannot find " + cardname)

class DeckDisplay(pg.Surface):
    _card_slot_images = {}
    
    def __init__(self, deck=None):
        super(DeckDisplay, self).__init__(size)

        #this won't work if a pygame display isn't initialised (TODO)
        self.load_images()

        if deck is None:
            #we want an empty deck
            self.deck = Deck()
        else:
            self.deck = deck

        self.fill(bgblue)

        self.show_cards()

    @classmethod
    def load_images(cls):
        #check to see if we've done this before
        if "fontM" in cls.__dict__:
            return
        
        if pg.font:
            if not pg.font.get_init():
                pg.font.init()

            cls.fontM = pg.font.SysFont("arial", 24, bold = True)
            cls.fontS = pg.font.SysFont("arial", 20, bold = True)

        cls.slot_blank = load_image("resource/slot_blank.png")

        #Numbers
        cls.numbers = {
            k: [textOutline(cls.fontM, str(i),
                            getattr(colors, k), colors.black)
                for i in range(100)]
            for k in ("yellow", "white")
            }

    @classmethod
    def get_card_slot_image(cls, cardname):
        #makes (or gets a premade) card slot image, WITHOUT quantity info
        if cardname in cls._card_slot_images:
            return cls._card_slot_images[cardname]

        fullcard = get_card(cardname)

        surface = cls.slot_blank.copy()

        mana = cls.numbers["white"][int(fullcard.cost)]
        surface.blit(mana, mana.get_rect(center=(18, 21)))

        name = textOutline(cls.fontS, fullcard.name,
                           colors.white, colors.black)
        surface.blit(name, name.get_rect(centery=21, left=42))

        cls._card_slot_images[cardname] = surface

        return surface

    def show_cards(self):
        #clear
        self.fill(bgblue)
        
        #draw the cards we have onto ourselves
        deck = sorted(self.deck["cards"].items(),
                      key=lambda x: int(get_card(x[0]).cost))
        
        for i, (card, quantity) in enumerate(deck):
            #copy so that we can add quantity without affecting the base
            card_img = self.get_card_slot_image(card).copy()

            q = self.numbers["yellow"][quantity]
            card_img.blit(q, q.get_rect(center=(width-18, 21)))

            self.blit(card_img, (0, CARD_HEIGHT*i))

    #interface directly with the deck
    def add_card(self, cardname):
        self.deck.add_card(cardname)

        self.show_cards()

    def take_card(self, cardname):
        self.deck.take_card(cardname)

        self.show_cards()
