import pandas as pd
import requests
import urllib
import re
from bs4 import BeautifulSoup
from app.extract_url.utils import url_extractor, url_to_df, df_to_url

class UrlExtraction():

    def __init__(self, url):

        self.main_url = url
        self.parsed_main_url = urllib.parse.urlparse(url)
        self.df_urls = url_to_df(url)
        self.urls = list(self.df_urls.index)
        self.nb_iteration = 0

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
        # Improvement: analyze all languange structure in url and define function instead written rules
        langs = {
            'fr':['fr','frfr'],
            'en':['en','enen'],
            'es':['es','eses'],
            'de':['de','dede'],
            'it':['it','itit'],
            'us':['us','usus']
        }
        langs[language] = []
        langs = sum(langs.values(),[])

        ind = self.df_urls.filter(regex=re.compile('(\/' + '\/|\/'.join(langs) + '\/)'), axis=0).index
        self.to_visit(ind, False)

        # Format selection: keep only .html and .php url
        ind = self.df_urls['path'].filter(regex=re.compile('(?!.*(.html|.php))\.[a-z]{2,6}$'), axis=0).index
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
        self.nb_iteration +=1
