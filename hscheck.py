import time
import re

#TODO: Secrets get apparently drawn twice

class HSLog():
    #does this really need to be a class? Can't all this just be top level?

    #normal draws
    reg = re.compile(r'\n\[Zone].*name=(.*) id=.* zone from FRIENDLY DECK.*\n')
    
    #initial draws
    gvgdraw = re.compile(r'\n\[Zone].*? id=1 .*name=(.*) id=.* zone from  -> FRIENDLY HAND.*\n')

    #cards returned during mulligan
    mul = re.compile(r'\n\[Zone].*name=(.*) id=.* zone from FRIENDLY HAND -> FRIENDLY DECK.*\n')

    #game result
    end = re.compile(r'\n\[Asset].*name=([a-z]+)_screen.*\n')

    f_path = r'C:\Program Files (x86)\Hearthstone\Hearthstone_Data\output_log.txt'

    def __init__(self):
        self.f = open(self.f_path, 'r')
        self.g = open(self.f_path, 'r')

        #go to the end, there's so much gubbins at the start
        self.f.seek(0, 2)

    def close_all(self):
        self.f.close()
        self.g.close()

    @property
    def drawn(self):
        x = self.f.read()
        
        c = self.reg.findall(x)
        m = self.mul.findall(x)
        g = self.gvgdraw.findall(x)

        out = {'d': c+g,
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
            return result[0]
        else:
            self.g.seek(-len(x), 1)
