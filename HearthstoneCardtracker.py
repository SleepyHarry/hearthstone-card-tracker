import pygame as pg
import os, sys, time, math, random, re
import copy
import json
from hscheck import *
from ctypes import windll

pg.init()

CARD_HEIGHT = 42
size = width, height = 245, CARD_HEIGHT*20
fps_tgt = 30
frame_delta = 1.0/fps_tgt
then = time.clock()

noframe = raw_input("Locked?").lower() in ["", "y", "yes", "true"]

if noframe:
    screen = pg.display.set_mode(size, pg.NOFRAME)
else:
    screen = pg.display.set_mode(size)

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
magenta = (255, 0, 255)
cyan = (0, 255, 255)
bgblue = (27, 30, 37)

swp = windll.user32.SetWindowPos

def topmost(flag=True):
    swp(pg.display.get_wm_info()['window'],
        -1 if flag else -2,
        1920 - width, 0, 0, 0, 0x0001)

above_all = True

topmost(above_all)

if pg.font:
    if not pg.font.get_init():
        pg.font.init()
    
    fontM = pg.font.SysFont("arial", 24, bold = True)
    fontS = pg.font.SysFont("arial", 20, bold = True)

def textHollow(font, message, fontcolor):
    notcolor = [c^0xFF for c in fontcolor]
    base = font.render(message, 0, fontcolor, notcolor)
    size = base.get_width() + 2, base.get_height() + 2
    img = pg.Surface(size, 16)
    img.fill(notcolor)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, notcolor)
    img.blit(base, (1, 1))
    img.set_colorkey(notcolor)
    return img

def textOutline(font, message, fontcolor, outlinecolor):
    base = font.render(message, 0, fontcolor)
    outline = textHollow(font, message, outlinecolor)
    img = pg.Surface(outline.get_size(), 16)
    colorkey = filter(lambda x: x not in [fontcolor, outlinecolor],
                      [magenta, black, white])[0]
    img.fill(colorkey)
    img.blit(base, (1, 1))
    img.blit(outline, (0, 0))
    img.set_colorkey(colorkey)
    return img

#render the numbers 0-9 in three colours, with a black outline
nums = {white: [], yellow: [], black: []}

for i in range(100):
    for k in nums:
        nums[k].append(textOutline(fontM, str(i), k, black))

def load_image(name, colorkey=None, alpha = False):
    fullname = os.path.join('resource/hs', name)
    try:
        image = pg.image.load(fullname)
    except pg.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message

    if alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()
    
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    
    return image, image.get_rect()

#Load all the card names and mana costs
with open("resource/hs/all-collectibles.json") as f:
    allCardsJSON = json.load(f)

allCards = [(x['name'], x['mana'], x['id']) for x in allCardsJSON['cards']]

class Card(object):
    def __init__(self, uid, name, manaCost, quantity=1):
        self.uid = uid
        self.name = name
        self.mana = manaCost
        self.quantity = quantity

        def f(s, c=white):
            return textOutline(fontS, str(s), c, black)
        
        self.rendered = {"name": (f(name), (40, 21)),
                         "mana": (nums[white][manaCost], (17, 21)),
                         "quantity": (nums[yellow][quantity], (226, 21))}

    def __eq__(self, vs):
        if self.name == vs.name:
            return True
        return False

    def loseOne(self):
        self.quantity -= 1

        self.rendered["quantity"] = (nums[yellow][self.quantity],
                                     (226, 21))

    def addOne(self):
        self.quantity +=1

        self.rendered["quantity"] = (nums[yellow][self.quantity],
                                     (226, 21))

    def draw(self, x, y):
        screen.blit(blank, (x,y))

        for k, v in self.rendered.items():
            if k=="quantity" and self.quantity==1:
                #don't bother drawing a '1'
                continue
            
            tgtX, tgtY = v[1]
            tgtC = (x+tgtX, y+tgtY)
            
            if k=="name":
                rect = v[0].get_rect(left=x+tgtX,
                                     centery=y+tgtY)
            else:
                rect = v[0].get_rect(center=(x+tgtX, y+tgtY))

            screen.blit(v[0], rect)

####
def remove_card(name, cards, quantity=1):
    if not quantity:
        return
    
    for card in cards:
        if name == card.name:
##            print "removing", name
            card.loseOne()
            break

    remove_card(name, cards, quantity-1)

def add_card(name, cards, quantity=1):
    if not quantity:
        return
    
    for card in cards:
        if name == card.name:
##            print "adding one of", name
            card.addOne()
            break
    else:
        cards.extend(parseDeck([name+",1"]))

        cards.sort(key=lambda x: x.name)
        cards.sort(key=lambda x: x.mana)

    add_card(name, cards, quantity-1)
####

offset = 0

def getDecks():
    print "getting decks"
    decks = map(lambda x: x[:-4], filter(lambda x: x[-4:]==".txt",
                                         os.listdir("resource/hs")))
    decknames = zip(decks, [textOutline(fontS, d, white, black) for d in decks])
    maxDecknameHeight = max(x[1].get_size()[1] for x in decknames)

    return decks, decknames, maxDecknameHeight

decks, decknames, maxDecknameHeight = getDecks()

def loadDeck(chosenDeck):
    try:
        with open("resource/hs/{}.txt".format(chosenDeck)) as f:
            deck = f.readlines()
    except:
        print "No such deck!"
        pg.quit()
        sys.exit()

    return deck

f_log = hs_log_setup()

#Parse the decklist, each line is in format [card],[quantity]\n
def parseDeck(deck):
    cards = []
    
    for line in deck:
        card, quantity = line.replace("\n", "").split(",")
##        print "{} x{}".format(card, quantity)
        quantity = int(quantity)
        try:
            cardJSON = filter(lambda x: x[0] == card, allCards)[0]
        except:
            print "no card {}".format(card)
            continue
        
        manaCost = cardJSON[1]
        uid = cardJSON[2]
        
        cards.append(Card(uid, card, manaCost, quantity))

    cards.sort(key = lambda x: x.name)
    cards.sort(key = lambda x: x.mana)

    return cards

#cards = parseDeck(deck)

def numCards(cards):
    return sum(x.quantity for x in cards)

deck = cards = []
drawn = []
highlighted = []

blank, blankRect = load_image("slotBlank.png")

highlight = pg.Surface((width, CARD_HEIGHT), pg.SRCALPHA)
highlight.fill((0, 255, 255, 25))

cachedImages = {}
drawStack = []

PREVIEW = False

pg.display.set_caption("HS Cardtracker")

#States: 1: choosing deck, 2: main tracker
STATE = 1

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            m1, m3, m2 = pg.mouse.get_pressed()
            
            mX, mY = pg.mouse.get_pos()

            if STATE == 1:
                #choosing deck
                #10+(maxDecknameHeight+4)*i
                selected = (mY-10)/(maxDecknameHeight+4)

                if selected in range(len(decks)):
                    deck = loadDeck(decks[selected])
                    cards = parseDeck(deck)
                    highlighted = []
                    offset = 0
                    
                    STATE = 2       #go to mulligan now a deck is selected
            elif STATE == 2:
                #main tracker
                mY -= offset
                
                if mY <= len(cards)*CARD_HEIGHT and m1:
                    #print "{} cards, mouse: ({}, {}), range height: {}"\
                    #      .format(len(cards), mX, mY, len(cards)*CARD_HEIGHT)
                    selectedCard = mY/CARD_HEIGHT
                    #print selectedCard, "of", len(cards)

                    if cards:
##                        try:
##                            c = cards[selectedCard]
##                            c.loseOne()
##                            add_card(c.name, drawn)
##                        except:
##                            print "Failed to remove card {}".format(selectedCard)
                        c = cards[selectedCard]
                        
                        if c in highlighted:
                            remove_card(c.name, highlighted, c.quantity)
                            print "removing", c
                        else:
                            add_card(c.name, highlighted, c.quantity)
                            print "adding", c

                if m2:
                    #reset the deck
                    print "\nResetting deck\n"
    
                    cards = parseDeck(deck)
                    drawn = []

                if event.dict['button'] == 4:
                    #scroll up
                    offset += 19
                elif event.dict['button'] == 5:
                    #scroll down
                    offset -= 19
        
        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()

            if keys[pg.K_ESCAPE]:
                pg.quit()
                sys.exit()

            if keys[pg.K_TAB]:
                above_all = not above_all
                topmost(above_all)

            if STATE == 1:
                if keys[pg.K_r]:
                    #reload decks
                    decks, decknames, maxDecknameHeight = getDecks()
            elif STATE == 2:
                if keys[pg.K_r]:
                    #reset the deck
                    print "\nResetting deck\n"
    
                    cards = parseDeck(deck)
                    drawn = []
                if keys[pg.K_BACKSPACE]:
                    STATE = 1

                    pg.display.set_caption("HS Cardtracker")
                if keys[pg.K_k]:
                    PREVIEW = not PREVIEW

    now = time.clock()
    if now-then < frame_delta:
        continue
    else:
        then = now

    if STATE == 1:
        screen.fill(bgblue)
        
        for i, (deckname, text) in enumerate(decknames):
            screen.blit(text, (10, 10+(maxDecknameHeight+4)*i))
    elif STATE == 2:
        ####
        result = check_result(f_log)

        if result in ['victory', 'defeat']:
            print "\ngame finished, result: {}\n".format(result)
            print "Resetting deck\n"
    
            cards = parseDeck(deck)
            drawn = []
            continue
        ####
        batch = cards_drawn(f_log)

        if batch['m']:
            #we've mulliganed
##            print "b[m]:", batch['m']
            for c in batch['m']:
                remove_card(c, drawn)
                add_card(c, cards)

        if batch['d']:
            #we've drawn a card
##            print "b[d]:", batch['d']
            for c in batch['d']:
                remove_card(c, cards)
                add_card(c, drawn)
                remove_card(c, highlighted)
        ####
        
        cards = filter(lambda x: x.quantity > 0, cards)
        drawn = filter(lambda x: x.quantity > 0, drawn)
        highlighted = filter(lambda x: x.quantity > 0, highlighted)

        offset = max(min(offset, 0), -((len(cards)-1)*CARD_HEIGHT))
        
        screen.fill(bgblue)

        #draw "cards"
        for i, card in enumerate(cards):
            card.draw(0, i*CARD_HEIGHT + offset)

            if card in highlighted:
                screen.blit(highlight, (0, i*CARD_HEIGHT + offset))

        #keep track of how many cards are left in the bottom right corner
        n = numCards(cards)

        try:
            p = 1.0/n
        except ZeroDivisionError:
            p = 0

        text = textOutline(fontS, "{} ({:.2%})".format(n, p),white, black)
        textrect = text.get_rect(right = width-10, bottom = height-10)

        screen.blit(text, textrect)

        pg.display.set_caption("{} ({:.2%})".format(n, p))

        #if any of the cards are selected, show the chance to draw one next turn
        if highlighted:
            p = numCards(highlighted)/float(n)

            text = textOutline(fontM, "{:.2%}".format(p), red, black)
            textrect = text.get_rect(centerx=width/2, bottom=height-40)

            screen.blit(text, textrect)

        mX, mY = pg.mouse.get_pos()
        oX, oY = mX, mY
        
        hoveredCard = (mY-offset)/CARD_HEIGHT

        if hoveredCard < len(cards) and cards and PREVIEW:
            uid = cards[hoveredCard].uid

            if not uid in cachedImages:
                img, imgRect = load_image("card images/{}.png".format(uid),
                                          alpha = True)
                cachedImages[uid] = img

            img = cachedImages[uid]
            w, h = img.get_size()
            mX = max(min(mX, width-w), 0)
            mY = max(min(mY, height-h), 0)

            imgRect = img.get_rect(top = mY+1)

            if imgRect.collidepoint(oX, oY):
                col = red
                mY = oY-h
            else:
                col = green
            
##            temp = pg.Surface((20, 20))
##            temp.set_colorkey(black)
##            pg.draw.circle(temp, col, (10, 10), 10)
##            drawStack.append((temp, (oX, oY)))
            
            drawStack.append((cachedImages[uid], (mX, mY)))
                

        while drawStack:
            img, pos = drawStack.pop()

            screen.blit(img, pos)
        
    pg.display.flip()


#TO-DO
    #sort out mulligans
    #animate (hold off on removing, keep highlighted or something
