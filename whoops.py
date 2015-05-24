""" Errors for Hearthstone tracker/Deck builder related things. """

class NoSuchDeckExists(Exception):
    pass

class DeckExistsWarning(Warning):
    pass

class CardNotInDeckError(Exception):
    pass
