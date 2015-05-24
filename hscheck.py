import re

from whoops import *

class HSLog:
    #does this really need to be a class? Can't all this just be top level?

    #normal draws
    reg = re.compile(
        r"\n\[Zone].*?name=(.*) id=([0-9]*).*? zone from FRIENDLY DECK.*?\n")

    #initial draws
    gvgdraw = re.compile(
        r"\n\[Zone].*? id=1 .*?name=(.*) id=([0-9]*).*? zone "
        r"from  -> FRIENDLY HAND.*?\n")

    #cards returned during mulligan
    mul = re.compile(
        r"\n\[Zone].*?name=(.*) id=([0-9]*).*? zone from "
        r"FRIENDLY HAND -> FRIENDLY DECK.*?\n")

    #game result
    end = re.compile(
        r"\n\[Asset].*name=([a-z]+)_screen.*\n")

    f_path = r"C:\Program Files (x86)\Hearthstone\Hearthstone_Data" \
             r"\output_log.txt"

    def __init__(self):
        self.f = open(self.f_path, 'r')
        self.g = open(self.f_path, 'r')

        #go to the end, there's so much gubbins at the start
        self.f.seek(0, 2)
        self.g.seek(0, 2)

        self.seen = {'c': set(),
                     'm': set(),
                     'g': set()}

    def close_all(self):
        self.f.close()
        self.g.close()

    def _process(self, name_id_pairs, flavour):
        """ make sure no duplicate ids are present

            we do this because for some reason, secrets look like they have
            been drawn twice, but the pair of "draws" always share an id. I
            believe (unconfirmed) that every truly unique draw has its own
            unique id, at least within a game.
        """
        for name, id in name_id_pairs:
            if id not in self.seen[flavour]:
                self.seen[flavour].add(id)
                yield name

    @property
    def drawn(self):
        x = self.f.read()

        c = list(self._process(self.reg.findall(x), 'c'))
        m = list(self._process(self.mul.findall(x), 'm'))
        g = list(self._process(self.gvgdraw.findall(x), 'g'))

        out = {'d': c + g,
               'm': m}

        if not (c or m or g):
            #no match, it's possible that the full line hasn't been written yet,
            #so track back and try again next loop

            #1 means move relative to where we are currently
            self.f.seek(-len(x), 1)

        return out

    @property
    def result(self):
        x = self.g.read()

        result = self.end.findall(x)

        if result:
            self.seen = {'c': set(),
                         'm': set(),
                         'g': set()}

            return result[0]
        else:
            self.g.seek(-len(x), 1)
