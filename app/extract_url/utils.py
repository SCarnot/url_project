import pandas as pd
import requests
import urllib
import re
import os
import sys
import json
from bs4 import BeautifulSoup

ROOT_DIR = os.path.abspath("")
sys.path.append(ROOT_DIR)  # To find local version of the library

# Define necessary fonctions
def make_the_soup(url):

    try:
        response = requests.get(url)
    except:
        # If the url is incorrect, return a simple soup ()'No response!') with no urls.
        return BeautifulSoup('No response!', 'html.parser')

    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def url_extractor(soup):

    list_url = list(filter(None,[a['href'] for a in soup.find_all(href=True)]))
    return list(set(list_url))

def url_to_df(url, to_visit=True, visited=False):

    if type(url)==str:
        url = [url]

    df_url = pd.DataFrame({
        'to_visit': True,
        'visited': False,
        'scheme': [urllib.parse.urlparse(u).scheme for u in url],
        'netloc': [urllib.parse.urlparse(u).netloc for u in url],
        'path': [urllib.parse.urlparse(u).path for u in url],
        'params': [urllib.parse.urlparse(u).params for u in url],
        'query': [urllib.parse.urlparse(u).query for u in url],
        'fragment': [urllib.parse.urlparse(u).fragment for u in url]
    }, index=url
    )

    return(df_url)

def df_to_url(df):

    url=[]
    for ind in df.index:
        url.append(
            urllib.parse.urlunparse(
                urllib.parse.ParseResult(
                    scheme=df.loc[ind,'scheme'],
                    netloc=df.loc[ind,'netloc'],
                    path=df.loc[ind,'path'],
                    params=df.loc[ind,'params'],
                    query=df.loc[ind,'query'],
                    fragment=df.loc[ind,'fragment']
                )
            )
        )

    return(url)

def init_features():

    col = ['nb_eur', 'nb_urls', 'bad_word', 'good_word', 'parent', 'nb_slash', 'end_length', 'url_length']

    return pd.DataFrame(columns=col)

def feature_extractor(url, soup, path_voc):

    with open(path_voc) as data_file:
        vocab = json.load(data_file, encoding='utf8')

    # Extract the end of the url for find interesting words and its size.
    regex_end_url = '\/(?!((.+)\/))(.+)' #Separate the last part of path's url
    if re.findall(regex_end_url, url):
        end_url = (re.findall(regex_end_url, url)[0][2])
    else:
        end_url = ''

    #Feature "bad_word" is set to 1 if one of those not interesting words is present in the url.
    forbidden_words = vocab['forbidden_words']
    regex_forbidden = '(' + forbidden_words[0]
    for voc in forbidden_words[1:]:
        regex_forbidden += '|' + voc
    regex_forbidden += ')s*(-|$|\.)'
    if re.search(re.compile(regex_forbidden) ,url.strip()):
        bad_word = 1
    else:
        bad_word = 0

    #Feature "good_word" is set to 1 if one of those intersting words is present in the url.
    interesting_words = sum(vocab['interesting_words'].values(),[])
    regex_interesting = '(-|^)(' + interesting_words[0]
    for voc in interesting_words[1:]:
        regex_interesting += '|' + voc
    regex_interesting += ')s*(-|$|\.)'
    if re.search(re.compile(regex_interesting) ,url.strip()):
        good_word = 1
    else:
        good_word=0

    #Measure the number of links to other url in the soup
    nb_urls = len(url_extractor(soup))

    # Url total Length
    url_length = len(url)

    # Length of the last string in the url
    end_length = len(end_url)

    # Number of '/'
    nb_slash = len(re.findall('(\/)',url))

    # Number of '€' symbol
    nb_eur = len(soup.find_all(string=re.compile('€')))
    parent = 0

    df_feature = pd.DataFrame({
        'nb_eur':[nb_eur],
        'nb_urls':[nb_urls],
        'bad_word':[bad_word],
        'good_word':[good_word],
        'parent':[parent],
        'nb_slash':[nb_slash],
        'end_length':[end_length],
        'url_length':[url_length],
        'url':url
        }).set_index('url')

    return df_feature
