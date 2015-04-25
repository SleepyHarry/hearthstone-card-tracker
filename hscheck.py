##import time
import re

#regexes
##card_move_regex = re.compile(r'\w*(cardId=(?P<Id>(\w*))).*(zone\ from\ '+\
##                             r'(?P<from>((\w*)\s*)*))((\ )*->\ (?P<to>('+\
##                             r'\w*\s*)*))*.*')
##zone_regex = re.compile(r'\w*(zone=(?P<zone>(\w*)).*(zone\ '+\
##                        'from\ FRIENDLY\ DECK)\w*)')
##opp_play_regex = re.compile(r'\w*(zonePos=(?P<zonePos>(\d+))).*(zone\ '+\
##                            'from\ OPPOSING\ HAND).*')
##hero_pow_regex = re.compile(r'".*(cardId=(?P<Id>(\w*))).*')

reg = re.compile(r'\n\[Zone].*name=(.*) id=.* zone from FRIENDLY DECK.*\n')
mul = re.compile(r'\n\[Zone].*name=(.*) id=.* zone from FRIENDLY HAND -> FRIENDLY DECK.*\n')

gvgdraw = re.compile(r'\n\[Zone].*name=(.*) id=.* zone from  -> FRIENDLY HAND.*\n')

end = re.compile(r'\n\[Asset].*name=([a-z]+)_screen.*\n')

def hs_log_setup():
    import time
    import re
    
##    test_str = '[Zone] ZoneChangeList.ProcessChanges() - id=94 local=False [name=Power Overwhelming id=30 zone=HAND zonePos=0 cardId=EX1_316 player=1] zone from FRIENDLY DECK -> FRIENDLY HAND'

    f_path = r'C:\Program Files (x86)\Hearthstone\Hearthstone_Data\output_log.txt'

    f = open(f_path, 'r')

    #go to the end, there's so much gubbins at the start
    f.seek(0, 2)

    return f

def cards_drawn(f):
    x = f.read()
    c = reg.findall(x)
    m = mul.findall(x)
    g = gvgdraw.findall(x)

    out = {'d': c+g,
           'm': m}

    if not (c or m or g):
        #no match, it's possible that the full line hasn't been written yet, so
        #track back and try again next loop
        f.seek(-len(x), 1)    #1 means move relative to where we are currently

    return out

def check_result(f):
    x = f.read()

    result = end.findall(x)

    if result:
        return result[0]
    else:
        f.seek(-len(x), 1)
        return
