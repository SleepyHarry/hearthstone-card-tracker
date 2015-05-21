import pygame as pg

import json

from useful import load_image, colors
from textFuncs import *

from hsd_util import Deck

bgblue = (27, 30, 37)

all_cards = json.load(open("resource/cards.json"))["cards"]

#This is not perfect. For example, "Misha" and "Devilsaur" were in here
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

    raise NoSuchCard("Cannot find {}".format(cardname))


class DeckContainer(pg.Surface):
    size = width, height = 0, 0

    def __init__(self, deck=None):
        super(DeckContainer, self).__init__(self.size)

        #this won't work if a pygame display isn't initialised (TODO)
        self._load_images()

        if deck is None:
            #we want an empty deck
            self.deck = Deck()
        else:
            self.deck = deck

        for k, v in vars(self.deck.__class__).items():
            #only get normal methods, not privates or dunders
            #also (deliberately) ignores classmethods
            if not k.startswith('_') and type(v) == type(lambda: None):
                setattr(self, k, self._deck_func(v))

        #TODO: should this be in the generic container?
        self.fill(bgblue)

    def _deck_func(self, func):
        """ Meant to be applied to functions from hsd_util.Deck

            This is used to enable interfacing directly with a
            DeckContainer's underlying deck, possible intercepting
            fucntionality. For example, DeckDisplay will want to update
            itself (DeckDisplay.show_cards()) whenever something happens
            to the underlying deck.

            DeckContainer._deck_func is simply a skeleton of this concept,
            in order to use it, override in subclasses and edit the inner
            function.
        """

        def inner(*args, **kwargs):
            #func is unbound
            func(self.deck, *args, **kwargs)

        return inner

    @classmethod
    def _load_images(cls):
        #TODO: make this extensible in subclasses?

        #check to see if we've done this before
        if "fontM" in cls.__dict__:
            return

        if pg.font:
            if not pg.font.get_init():
                pg.font.init()

            cls.fontM = pg.font.SysFont("arial", 24, bold=True)
            cls.fontS = pg.font.SysFont("arial", 20, bold=True)

        cls.slot_blank = load_image("resource/slot_blank.png")

        #Numbers
        cls.numbers = {
            k: [textOutline(cls.fontM, str(i),
                            getattr(colors, k), colors.black)
                for i in range(100)]
            for k in ("yellow", "white")
            }

    @classmethod
    def _get_card_slot_image(cls, cardname):
        """makes (or gets a premade) card slot image, WITHOUT quantity info"""

        if cardname in cls._card_slot_images:
            return cls._card_slot_images[cardname]

        ##        print cardname

        fullcard = get_card(cardname)

        surface = cls.slot_blank.copy()

        mana = cls.numbers["white"][int(fullcard.cost)]
        surface.blit(mana, mana.get_rect(center=(18, 21)))

        name = textOutline(cls.fontS, fullcard.name,
                           colors.white, colors.black)
        surface.blit(name, name.get_rect(centery=21, left=42))

        cls._card_slot_images[cardname] = surface

        return surface

class DeckDisplay(DeckContainer):
    _card_slot_images = {}

    CARD_HEIGHT = 42
    width = 245
    height_in_cards = 24.5

    def __init__(self, deck=None, height_in_cards=None):
        self.size = (self.width,
                (height_in_cards or self.height_in_cards) * self.CARD_HEIGHT)
        super(DeckDisplay, self).__init__(deck)

        self.show_cards()

    def _deck_func(self, func):
        def inner(*args, **kwargs):
            #func is unbound
            func(self.deck, *args, **kwargs)

            self.show_cards()

        return inner

    def show_cards(self):
        #clear
        self.fill(bgblue)

        deck = sorted(self.deck["cards"].items(),
                      key=lambda x: int(get_card(x[0]).cost))

        #draw the cards we have onto ourselves
        for i, (card, quantity) in enumerate(deck):
            #copy so that we can add quantity without affecting the base
            card_img = self._get_card_slot_image(card).copy()

            q = self.numbers["yellow"][quantity]
            card_img.blit(q, q.get_rect(center=(self.width - 18, 21)))

            self.blit(card_img, (0, self.CARD_HEIGHT * i))


class ManaCurve(DeckContainer):
    size = width, height = 400, 300  #TODO: finalise these