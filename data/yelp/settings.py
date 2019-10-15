import os

from . import util

# Local storage
PROGRESS_PATH = util.localize_path('businesses_search_progress.json')
SEARCH_API_DATA_PATH = util.localize_path('businesses_search.json')

# Yelp API auth
YELP_APP_ID = 'JIHiA3VnvdRPHoeZRKfBCA'
YELP_API_SECRET = os.environ.get("YELP_API_SECRET", None)
YELP_AUTH_HEADER = {'Authorization': 'Bearer %s' % YELP_API_SECRET}
