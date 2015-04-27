import json
import requests
import re

from collections import namedtuple, defaultdict
from BeautifulSoup import BeautifulSoup as bs

url = ("http://www.hearthpwn.com/cards?filter-unreleased=1&&"
                                    "display=1&page={page}")

Card = namedtuple("Card", "name type race cost attack health "
                          "rarity set")

class ConnectionError(Exception):
    pass

def get_soup(page):
    response = requests.get(url.format(page=page))

    if not response.ok:
        raise ConnectionError

    return bs(response.text)

def get_rows(soup):
    return (row for row in soup.findAll("tr") if row.has_key("class"))

def html_unescape(text):
    #not going for the full thing, just enough to cover the cases encountered
    escapes = {
        "&nbsp;": "",    #are there and ampersands in card names?
        "&#x27;": "'",
        }

    for before, after in escapes.items():
        text = text.replace(before, after)

    return text

def process_card(row):
    tds = row.childGenerator()

    other_info = dict(row.first('a').attrs)

    rarity, card_set = re.match(r"rarity-([0-9]+) set-([0-9]+).*",
                                other_info["class"]).groups()

    return Card(*([html_unescape(td.getText()) for td in tds] + \
                  [rarity, card_set]))

def main(quiet=True):
    cards = defaultdict(dict)
    
    for page in range(1, 12):
        try:
            for i, entry in enumerate(get_rows(get_soup(page))):
                try:
                    if not quiet:
                        print ("Fetching page {}, "
                               "entry {}/100").format(page, i+1)

                    card = process_card(entry)
                    cards[card.type][card.name] = card._asdict()
                except Exception, e:
                    #no idea, keep going and deal with it later
                    print e
        except ConnectionError:
            print "Couldn't connect to page", page

    with open("resource/cards.json", 'w') as f:
        json.dump({"cards": cards}, f)
