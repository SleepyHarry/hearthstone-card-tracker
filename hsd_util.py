''' Does everything to do with the .hsd file format

    The goal of this to faciliate the loading and saving of Hearthstone decks,
    by providing a high-level API with .hsd files, thus meaning that we don't
    have to deal with deck-related files anywhere but here

    Under the covers, .hsd are simply pickles of Deck objects, which themselves
    are just glorified dicts
'''

import os
import pickle
from collections import Counter

class NoSuchDeckExists(Exception):
    pass

class DeckExistsWarning(Warning):
    pass

class CardNotInDeckError(Exception):
    pass

class Deck(dict):
    def __init__(self, cards=None, hero='', fmt=''):
        #we can supply a Counter or a sequence iterable
        if cards is None:
            #we want an empty deck
            cards = dict()

        self._history = []
        self._reset_additions = []
        
        self["cards"] = Counter(cards)
        
        self["hero"] = hero
        self["format"] = fmt

    def __repr__(self):
        return ("{}(".format(self.__class__.__name__) +
                ", ".join("{}={}".format(k, repr(v)) for k, v in
                                  self.items()) +
                ")")

    def add_card(self, cardname):
        self["cards"][cardname] += 1

        self._history.append(cardname)

    def add_again(self):
        if self._history:
            self.add_card(self._history[-1])

    def take_card(self, cardname, remember=False):
        """ Takes a card (specified by cardname) out of the deck.
            if remember is True, make a note of it so that when we
            call reset, we replace every card we took out (and remembered)
        """
        
        #TODO: Clean this up. Four references to self["cards"][cardname] is
        #      silly
        if cardname == "The Coin":
            return
        elif self["cards"][cardname] <= 0:
            raise CardNotInDeckError('"{}"'.format(cardname))

        self["cards"][cardname] -= 1

        if self["cards"][cardname] == 0:
            del self["cards"][cardname]

        if remember:
            self._reset_additions.append(cardname)

    def take_last(self):
        if self._history:
            self.take_card(self._history.pop())

    def clear(self):
        self["cards"] = Counter()
        self["hero"] = ''
        self["format"] = ''

        self._history = []
        self._reset_additions = []

    def reset(self):
        """ Replace every card we took out and remembered """

        while self._reset_additions:
            self.add_card(self._reset_additions.pop())

    def __len__(self):
        return sum(self["cards"].values())

    def replace(self, new_deck):
        """ Given a Deck-like object new_deck, make us like it IN PLACE """
        self.clear()
        self.update(new_deck)

    def save(self, filename, force=False):
        if not force and os.path.exists(filename):
            #attempting to overwrite
            raise DeckExistsWarning(("Attempting to overwrite deck at {}, "
                                     "use force=True to supress this warning.")
                                    .format(os.path.abspath(filename)))

        #should we be catching OSErrors here?
        pickle.dump(dict(self), open(filename, 'w'))

    to_hsd = save    #this seems like a good idea
    
    @classmethod
    def from_hsd(cls, filename):
        if not os.path.exists(filename):
            raise NoSuchDeckExists("Cannot find deck at {}"
                                   .format(os.path.abspath(filename)))

        new_deck = cls()
        old_deck = pickle.load(open(filename))

        new_deck.replace(old_deck)

        return new_deck
