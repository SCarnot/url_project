import pandas as pd
import requests
import urllib
import re
import sys
import os
import json

ROOT_DIR = os.path.abspath("")
sys.path.append(ROOT_DIR)  # To find local version of the library

from bs4 import BeautifulSoup
from app.extract_url.utils import url_extractor, url_to_df, df_to_url, make_the_soup, init_features, feature_extractor

class UrlExtraction():

    def __init__(self, url, ROOT_DIR):

        self.main_url = url
        self.parsed_main_url = urllib.parse.urlparse(url)
        self.df_urls = url_to_df(url)
        self.df_features = init_features()
        self.urls = list(self.df_urls.index)
        self.nb_iteration = 0
        self.ROOT_DIR = ROOT_DIR

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

    def add_features(self, feat):

        self.df_features = self.df_features.append(feat)

    def extract_new_url(self):

        visiting_list = list(self.df_urls[self.df_urls['to_visit']==True].index)
        print('Number of url to visit :', len(visiting_list))

        path_voc = self.ROOT_DIR + "/data/ressources/vocabulary.json"
        for url in visiting_list:
            print('Visiting url', url)
            new_soup = make_the_soup(url)
            self.visited(url, True)
            self.add_url(url_extractor(new_soup))
            self.add_features(feature_extractor(url, new_soup, path_voc))

    def raw_cleaning(self):

        # Build empty netloc url
        ind_netloc = self.df_urls[self.df_urls['netloc']==''].index
        self.df_urls.loc[ind_netloc,'scheme'] = self.parsed_main_url.scheme
        self.df_urls.loc[ind_netloc,'netloc'] = self.parsed_main_url.netloc

        # Ensure path begins with a '/'
        self.df_urls.loc[ind_netloc,'path'] = self.df_urls.loc[ind_netloc,'path'].apply(lambda x : ('/' + x).replace('//','/'))

        self.df_urls = self.df_urls.drop_duplicates(
            subset=['scheme', 'netloc', 'path', 'params', 'query', 'fragment'])

        self.df_urls.index = df_to_url(self.df_urls)

        #Drop external netloc
        self.drop_url(self.df_urls[self.df_urls['netloc']!=self.parsed_main_url.netloc].index)
        #Drop other scheme
        self.drop_url(self.df_urls[self.df_urls['scheme']!=self.parsed_main_url.scheme].index)
        #Drop empty path
        self.drop_url(self.df_urls[self.df_urls['path']==''].index)

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
        self.nb_iteration += 1

    def full_iteration(self, n_it=12):

        while (self.df_urls[self.df_urls['to_visit']==True].shape[0] > 0) and (self.nb_iteration < n_it):
            print('Iteration:', self.nb_iteration)
            self.iteration()
        if self.nb_iteration == n_it :
            print('Max. iterations reached')

if __name__ == '__main__':

    path_urls = ROOT_DIR + '/data/ressources/url_examples.json'

    #Create dump file if not created (not tracked by git)
    if not os.path.exists(ROOT_DIR + '/data/dump/'):
        os.makedirs(ROOT_DIR + '/data/dump/')

    with open(path_urls) as data_file:
        urls = json.load(data_file, encoding='utf8')

    for key, value in urls.items():

        print('Website visited:', value)
        Url = UrlExtraction(value, ROOT_DIR)
        Url.full_iteration()
        file_name = ROOT_DIR + '/data/dump/' + key + '.csv'
        Url.df_features.to_csv(file_name)
