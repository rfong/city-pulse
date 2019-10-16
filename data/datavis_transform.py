'''
Script to transform downloaded data to a format usable for my datavis.
This assumes you have already run the fetcher script and have some data
downloaded.

+ heatmap points: `[lat, lng, intensity]`
'''

import json
import os
import time

from yelp.settings import *


def to_points(
    value_selector, value_transform_fn=None, ignore_nulls=False,
    restrict_to_city=None
):
    '''
    Transforms business data into a list of points to be used on a map; that
    is, coordinates with an associated value.

    `value_selector` is a dictionary key into a Yelp business API object.
    Point format:
        `[lat, lng, value]`
    '''
    if value_transform_fn is None:
        def value_transform_fn(x): return x  # Identity function

    def should_keep_biz(biz):
        # Check if value is null
        if biz.get(value_selector) is None and not ignore_nulls:
            return False
        # Check if city doesn't match
        if restrict_to_city:
            if (biz['location']['city'].lower().replace(' ', '') !=
                    restrict_to_city.lower().replace(' ', '')):
                return False
        return True

    return [
        [
            b['coordinates']['latitude'],
            b['coordinates']['longitude'],
            value_transform_fn(b.get(value_selector)),
        ]
        for id, b in list(get_business_data().items())
        if should_keep_biz(b)
    ]


def write_heatmap_points(rel_path, points):
    path = os.path.join(os.path.dirname(__file__), rel_path)
    with open(path, 'w') as f:
        f.write(json.dumps(points))


business_data_cache = None
business_data_cached_path = None


def get_business_data(path=None):
    '''
    Fetch all business data from local storage.
    '''
    if path is None:
        path = SEARCH_API_DATA_PATH

    global business_data_cache, business_data_cached_path
    if business_data_cache is None or path != business_data_cached_path:
        with open(path, 'r') as f:
            business_data_cache = json.loads(f.read())
            business_data_cached_path = path

    return business_data_cache


if __name__ == '__main__':
    city = 'San Francisco'
    write_heatmap_points(
        'yelp_price_points.json',
        to_points('price', lambda price: len(price), restrict_to_city=city)
    )

    write_heatmap_points(
        'yelp_rating_points.json',
        to_points('rating', restrict_to_city=city)
    )

    write_heatmap_points(
        'yelp_review_count_points.json',
        to_points('review_count', restrict_to_city=city)
    )
