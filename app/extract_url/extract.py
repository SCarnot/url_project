import pandas as pd
import requests
import urllib
import re
from bs4 import BeautifulSoup

# Define necessary fonctions
def url_extractor(url):

    # Améliorer le try/except
    try:
        response = requests.get(url)
    except:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
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

class UrlExtraction():

    def __init__(self, url):

        self.main_url = url
        self.parsed_main_url = urllib.parse.urlparse(url)
        self.df_urls = url_to_df(url)
        self.urls = list(self.df_urls.index)
        self.iteration = 0

    def add_url(self, url):

        self.df_urls = self.df_urls.append(url_to_df(url)).drop_duplicates()
        self.urls = list(self.df_urls.index)

    def drop_url(self, url):

        self.df_urls = self.df_urls.drop(url)
        self.urls = list(self.df_urls.index)

    def to_visit(self, url, action):

        self.df_urls.loc[url, 'to_visit'] = action

    def visited(self, url, action):

        self.df_urls.loc[url, 'visited'] = action
        self.df_urls.loc[url, 'to_visit'] = not action

    def raw_cleaning(self):

        # Build empty netloc url
        ind_netloc = self.df_urls[self.df_urls['netloc']==''].index
        self.df_urls.loc[ind_netloc,'scheme'] = self.parsed_main_url.scheme
        self.df_urls.loc[ind_netloc,'netloc'] = self.parsed_main_url.netloc
        self.df_urls = self.df_urls.drop_duplicates(
            subset=['scheme', 'netloc', 'path', 'params', 'query', 'fragment'])
        self.df_urls.index = df_to_url(self.df_urls)

        #Drop external netloc
        self.drop_url(self.df_urls[self.df_urls['netloc']!=self.parsed_main_url.netloc].index)
        #Drop other scheme
        self.drop_url(self.df_urls[self.df_urls['scheme']!=self.parsed_main_url.scheme].index)
        #Drop empty path
        self.drop_url(self.df_urls[self.df_urls['path']==''].index)

    def extract_new_url(self):

        visiting_list = list(self.df_urls[self.df_urls['to_visit']==True].index)
        print('Number of url to visit :', len(visiting_list))

        for url in visiting_list:
            print('Visiting url', url)
            self.visited(url, True)
            self.add_url(url_extractor(url))

    def raw_filtering(self, language='fr'):

        # Language selection
        langs = ['fr', 'en', 'es', 'de', 'it', 'us']
        langs.remove(language)
        ind = self.df_urls.filter(regex=re.compile('(\/' + '\/|\/'.join(langs) + '\/)'), axis=0).index
        self.to_visit(ind, False)

        # Disable fragment
        ind = self.df_urls[self.df_urls['fragment']!=''].index
        self.to_visit(ind, False)

        # Disable query
        ind = self.df_urls[self.df_urls['query']!=''].index
        self.to_visit(ind, False)

    def iteration(self):

        self.extract_new_url()
        self.raw_cleaning()
        self.raw_filtering()
        self.iteration +=1
