import requests
import urllib
import re
from bs4 import BeautifulSoup

def string_to_price(string):
    regex_complex = ('^('
                     '(€|euro|£)*\s*([0-9]{1,4})((,|\.)([0-9]{0,2}))*\s*(€|euro|£)*'
                     ')$')
    reg = re.search(regex_complex, string)
    if reg:
        if reg.groups()[5]:
            return int(reg.groups()[2])+0.01*int(reg.groups()[5])
        else:
            return int(reg.groups()[2])
    else:
        return None

def price_extraction(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    it = 0
    # Extract all <span> where the currency appears
    price = (soup.find_all('span', string=re.compile('(€|euro|£)')) +
             soup.find_all('div', string=re.compile('(€|euro|£)')) +
             soup.find_all('h2', string=re.compile('(€|euro|£)'))
            )
    if len(list(price))==0:
        price = soup.find_all('div', string=re.compile('(€|euro|£)'))
    price = [string_to_price(el.string.strip()) for el in price]

    while 0.0 in price:
        price.remove(0.0)

    return list(filter(None, price))
