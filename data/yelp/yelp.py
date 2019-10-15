'''
Fetch data from Yelp API such that we circumvent the download limits and can
pause/resume progress when we are rate limited or crash.
'''

from enum import Enum
import json
import logging
import os
import pprint
import requests
import sys
import tempfile

from . import util
from . import persist
from .progress import ProgressMeter, ProgressStatus
from .settings import *
from . import yelp_categories

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Constants
class MyError(Enum):
    API_ERROR = 1
    API_EXCEEDED_FETCH_LIMIT = 2

# Yelp API constants
YELP_SEARCH_API_URL = 'https://api.yelp.com/v3/businesses/search'

YELP_MAX_FETCH_LIMIT = 1000
YELP_REQUEST_FETCH_LIMIT = 50


class Fetcher(object):

    # Auth

    def __init__(self, is_test=False):
        tlc = yelp_categories.get_top_level_categories()
    
        if is_test:
            self.progress = ProgressMeter(tempfile.TemporaryFile().name)
            self.search_data_path = tempfile.TemporaryFile().name
        else:
            self.progress = ProgressMeter(PROGRESS_PATH)
            self.search_data_path = SEARCH_API_DATA_PATH

        self.progress.add_keys(tlc)  # This won't overwrite existing progress
   
    def persist_search_results(self, response_json):
        '''
        Persist data from the Yelp v3/businesses/search API to local JSON.
        Save format: key value store where
            key = unique yelp business ID
            value = JSON representation of business as returned by API
        '''
        def my_update_fn(old_data, new_data):
            '''Update dict with 'id' field as key'''
            for biz in new_data:
                old_data[biz.get('id')] = biz
            return old_data
        persist.update_json_file(
            self.search_data_path,
            response_json.get('businesses'),
            update_fn=my_update_fn)

    def fetch_all_businesses(self):
        complete_categories = [
            k for k,v in self.progress.get_data().items()
            if v is ProgressStatus.COMPLETE
        ]
        print("complete categories", len(complete_categories))

        incomplete_categories = [
            k for k,v in self.progress.get_data().items()
            if v is ProgressStatus.INCOMPLETE
        ]
        print("incomplete categories", len(incomplete_categories))

        for cat in incomplete_categories:
            #search_category = 'convenience'  # 235
            #search_category = 'food'  # 3500
            params = {
                'location': 'San Francisco',
                'term': '',
                'offset': 0,
                'limit': YELP_REQUEST_FETCH_LIMIT,
                #'open_at': 1571081461,
                'categories': cat,
                #'pricing_filter': '1, 2',
                #'sort_by': 'rating',
            }
            self.fetch_businesses_by_params(params)
    
    def fetch_businesses_by_params(self, params):
        category = params.get('categories')

        if self.progress.is_complete(category) == True:
            logger.info(
                "Category %s is already completed. Skipping." % category)
            return
        if self.progress.is_wontfix(category) == True:
            logger.info("Category %s is marked wontfix. Skipping." % category)
            return

        # Make API request
        resp = requests.get(
            url=YELP_SEARCH_API_URL, params=params, headers=YELP_AUTH_HEADER)
        if resp.json().get('error') is not None:
            logger.error(
                'API error - %s' % resp.json()['error'].get('description'))
            pprint.pprint(resp.json())
            return
    
        # Dump business info
        total = resp.json()['total']
        if params['offset'] == 0:
            logger.info("Category %s - %d results" % (category, total))
        if total == 0:
            self.progress.mark_complete(category)
            return

        # Save data
        self.persist_search_results(resp.json())
       
        # If within API single request limit, return current results.
        if total <= YELP_REQUEST_FETCH_LIMIT:
            self.progress.mark_complete(category)
            return
        # If we need to fetch more but within the API limit, fetch them all now.
        if total <= YELP_MAX_FETCH_LIMIT:
            if params['offset'] + params['limit'] >= total:
                self.progress.mark_complete(category)
                return
            params['offset'] += YELP_REQUEST_FETCH_LIMIT
            logger.info("Fetch next page; offset=%d" % params['offset'])
            self.fetch_businesses_by_params(params)
            return
  
        # Otherwise, must narrow down search to get under API limit.
        logger.info("\tExceeded API limit. Narrowing down search.")
        category = params.get('categories', '')
        child_categories = yelp_categories.get_child_categories(category)

        if child_categories is []:
            raise Exception((
                "Data for category %s cannot be fully fetched because it has "
                 "no child categories and exceeds API limit"
            ) % category)

        # Mark parent category as wontfix, and add the new categories to try.
        self.progress.mark_wontfix(category)
        self.progress.add_keys(child_categories)
        return None, []
            
    def multi_fetch_businesses_by_params(self, params, total_results):
        '''
        The number of business results spanned by this request exceeds the
        per-request limit, but fits within the max API limit. Fetch until we have
        all of them.
        '''
        params['limit'] = YELP_REQUEST_FETCH_LIMIT
        for offset in range(
            YELP_REQUEST_FETCH_LIMIT, total_results, YELP_REQUEST_FETCH_LIMIT
        ):
            params['offset'] = offset
            print('TODO: Fetch at offset=%d' % offset)
            self.fetch_businesses_by_params(params)
    

def main():
    Fetcher().fetch_all_businesses()

