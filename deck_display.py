import pygame as pg

import json

from collections import Counter

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


class ObservableDeck(Deck):
    """ Same as Deck, except it knows everything observing it, and notifies
        them when something happens.
    """

    def __init__(self, cards=None, hero='', fmt='',
                 observers=None):
        """ obsevers should be an iterable if not None
        """
        super(ObservableDeck, self).__init__(cards, hero, fmt)

        self.observers = observers or []

        for k, v in vars(Deck).items():
            #only get normal methods, not privates or dunders
            #also (deliberately) ignores classmethods
            if not k.startswith('_') and type(v) == type(lambda: None):
                setattr(self, k, self._deck_func(v))

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def _deck_func(self, func):
        """ Meant to be applied to functions from hsd_util.Deck

            This is used to enable interfacing directly with a DeckObserver's
            underlying deck, possibly intercepting functionality if
            overridden.

            DeckObserver._deck_func is simply a skeleton of this concept,
            intercepting only to call the (possibly not overidden)
            self.update method.
        """

        def inner(*args, **kwargs):
            #func is unbound
            func(self, *args, **kwargs)

            self.notify_observers()

        return inner


class DeckObserver(pg.Surface):
    size = width, height = 0, 0

    def __init__(self, deck=None):
        super(DeckObserver, self).__init__(self.size)

        #this won't work if a pygame display isn't initialised (TODO)
        self._load_images()
        self._load_extra_images()

        if deck is None:
            #we want an empty deck
            self.deck = ObservableDeck()
        else:
            self.deck = deck

        self.deck.add_observer(self)

        self.update()

    def update(self):
        #TODO: should this be in the generic container?
        self.fill(bgblue)

    @classmethod
    def _load_images(cls):
        #check to see if we've done this before
        if "fontM" in cls.__dict__:
            return

        if pg.font:
            if not pg.font.get_init():
                pg.font.init()

            cls.fontM = pg.font.SysFont("arial", 24, bold=True)
            cls.fontS = pg.font.SysFont("arial", 20, bold=True)

        #Numbers
        cls.numbers = {
            k: [textOutline(cls.fontM, str(i),
                            getattr(colors, k), colors.black)
                for i in range(100)]
            for k in ("yellow", "white")
            }

    @classmethod
    def _load_extra_images(cls):
        """ Load images specific to this container
        """

        #No extras in the base class, obviously
        pass

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


class DeckDisplay(DeckObserver):
    _card_slot_images = {}

    CARD_HEIGHT = 42
    width = 245
    height_in_cards = 24.5

    def __init__(self, deck=None, height_in_cards=None):
        self.size = (
            self.width,
            (height_in_cards or self.height_in_cards) * self.CARD_HEIGHT
        )
        super(DeckDisplay, self).__init__(deck)

        self.update()

    @classmethod
    def _load_extra_images(cls):
        """ Load images specific to this observer
        """
        cls.slot_blank = load_image("resource/slot_blank.png")

    def update(self):
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


class ManaCurve(DeckObserver):
    size = width, height = 320, 280  #TODO: finalise these

    def __init__(self, deck=None):
        super(ManaCurve, self).__init__(deck)

        self._draw_static_canvas()

    @classmethod
    def _load_extra_images(cls):
        """ Load images specific to this container
        """
        cls.mana_gem = load_image("resource/mana_gem.png",
                                  colorkey=colors.magenta)

        cls.numbers["7+"] = textOutline(cls.fontM, "7+",
                                        colors.white, colors.black)

    def _draw_static_canvas(self):
        """ Draw the base of the ManaCurve, which is always present """
        self.fill(colors.yellow)
        self.fill(bgblue, (1, 1, self.width - 2, self.height - 2))

        for i in xrange(8):
            center = (int((i + .5) * self.width / 8), self.height - 20)
            self.blit(self.mana_gem,
                      self.mana_gem.get_rect(center=center))

            if i != 7:
                num = self.numbers["white"][i]
            else:
                num = self.numbers["7+"]

            self.blit(num, num.get_rect(center=center))

    def update(self):
        self.fill(bgblue, (1, 1, self.width - 2, self.height - 37))

        cost_breakdown = Counter()

        for k, v in self.deck["cards"].items():
            cost = get_card(k).cost

            cost_breakdown[min(int(cost), 7)] += v

        if cost_breakdown:
            highest = max(cost_breakdown.values())
            modifier = 1 if not highest > 4 else 4./highest

        for k, v in cost_breakdown.items():
            #TODO: bars
            width = 30
            height = int(50 * v * modifier)
            left = int((k + .5) * self.width / 8 - width/2.)
            top = self.height - 40 - height

            bar_rect = pg.Rect(left, top, width, height)
            bar_inner_rect = pg.Rect(bar_rect.left + 1,
                                     bar_rect.top + 1,
                                     bar_rect.width - 2,
                                     bar_rect.height - 2)

            self.fill((128, 128, 0), bar_rect)
            self.fill(colors.yellow, bar_inner_rect)
            # self.blit(self.numbers["yellow"][v],
            #           (int((k + .5) * self.width / 8), self.height / 2))
