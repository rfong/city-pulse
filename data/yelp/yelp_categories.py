'''
Convenience methods over all Yelp API categories, as downloaded from:
    https://www.yelp.com/developers/documentation/v3/all_category_list
'''

import json

from . import util

all_categories = None
top_level_categories = None


def load_categories():
    '''Load all Yelp categories into global namespace'''
    global all_categories, top_level_categories

    if all_categories is None:
        with open(util.localize_path('categories.json'), 'r') as f:
            all_categories = json.loads(f.read())  # All yelp categories

    if top_level_categories is None:
        top_level_categories = [
            c['alias'] for c in
            filter(lambda c: c.get('parents', []) == [], all_categories)
        ]


def get_top_level_categories():
    load_categories()
    return top_level_categories


def get_child_categories(parent_category):
    load_categories()
    return [
        c['alias'] for c in filter(
            lambda c: parent_category in c.get('parents', []), all_categories
        )
    ]
