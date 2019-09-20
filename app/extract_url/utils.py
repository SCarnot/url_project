import pandas as pd
import requests
import urllib
import re
from bs4 import BeautifulSoup

# Define necessary fonctions
def make_the_soup(url):

    try:
        response = requests.get(url)
    except:
        return []

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

def feature_extractor(url, soup):

    #Feature "bad_word" is set to 1 if one of those not interesting words is present in the url.
    forbidden_words = ['carte', 'mention', 'fondateur', 'register', 'condition', 'cgv', 'livraison', 'politique', 'login'
     'guide', 'taille', 'contact', 'account', 'marque', 'journal', 'book']
    bad_word = 0
    for wrd in forbidden_words:
        if wrd in urllib.parse.urlparse(url).path:
            bad_word = 1

    #Feature "good_word" is set to 1 if one of those intersting words is present in the url.
    interesting_words = ['chaussure', 'mocassin', 'pull', 'shirt', 'pantalon', 'veste', 'chemise', 'blouson', 'sneakers']
    regex_end_url = '\/(?!((.+)\/))(.+)' #Separate the last part of path's url
    good_word = 0
    if re.search(regex_end_url, url):
        for wrd in interesting_words:
            if wrd in re.findall(regex_end_url,url)[0][2]:
                good_word = 1

    #Measure the number of links to other url in the soup
    nb_urls = len(url_extractor(soup))

    # Url total Length
    url_length = len(url)

    # Length of the last string in the url
    end_length = 0
    if re.search(regex_end_url, url):
        end_length = len(re.findall(regex_end_url, url)[0][2])

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
