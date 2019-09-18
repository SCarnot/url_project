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
