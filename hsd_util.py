''' Does everything to do with the .hsd file format

    The goal of this to faciliate the loading and saving of Hearthstone decks,
    by providing a high-level API with .hsd files

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

class Deck(dict):
    def __init__(self, cards, hero='', fmt=''):
        if issubclass(type(cards), Counter):
            self["cards"] = cards
        else:
            self["cards"] = Counter(cards)

        self["hero"] = hero
        self["format"] = fmt

    def save(self, filename, force=False):
        if not force and os.path.exists(filename):
            #attempting to overwrite
            raise DeckExistsWarning(("Attempting to overwrite deck at {}, "
                                     "use force=True to supress this warning.")
                                    .format(os.path.abspath(filename)))

        #should we be catching OSErrors here?
        pickle.dump(self, open(filename, 'w'))

    to_hsd = save    #this seems like a good idea
    
    @classmethod
    def from_hsd(cls, filename):
        if not os.path.exists(filename):
            raise NoSuchDeckExists("Cannot find deck at {}"
                                   .format(os.path.abspath(filename)))

        deck_dict = pickle.load(open(filename))
        
        return cls(deck_dict["cards"],
                   deck_dict["hero"],
                   deck_dict["format"])
