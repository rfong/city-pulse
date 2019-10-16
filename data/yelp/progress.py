'''
A progress meter in local storage to keep track of multipart / paramaterized
downloads so that we can explore API param configurations that aren't limited
by the download limit.
'''

import json
import logging
import os

from . import persist
from . import util

logger = logging.getLogger(__name__)


class ProgressStatus:
    INCOMPLETE = 1
    COMPLETE = 2
    # WONTFIX: for example, when we shouldn't try a parameter value again
    # because it exceeds the API limit and its results need to be broken into
    # smaller chunks.
    WONTFIX = 3


class ProgressMeter():
    '''
    Persist an ongoing progress record to local filesystem.
    This allows us to pick up where we left off if we exceed the daily API
    limit.
    Save format:
        {<key>: <ProgressStatus>}
    '''
    data = None

    def __init__(self, path):
        '''
        Get a new ProgressMeter instance.
        If no path set, use the default path.
        If file does not exist, instantiate.
        '''
        self.path = path
        try:
            self.get_data()
        except FileNotFoundError:
            self.destructive_reset([])

    def refresh_data(self):
        '''Update cache'''
        with open(self.path, 'r') as f:
            self.data = json.loads(f.read()) or {}

    # Read-only

    def get_data(self):
        '''Return all progress data. Cache.'''
        if self.data is None:
            self.refresh_data()
        return self.data

    def keys(self):
        '''Return all keys'''
        return list(self.get_data().keys())

    def get_value(self, key):
        '''Return outcome for a specific key.'''
        return self.get_data().get(key, None)

    def is_complete(self, key):
        return self.get_value(key) == ProgressStatus.COMPLETE

    def is_incomplete(self, key):
        return self.get_value(key) == ProgressStatus.INCOMPLETE

    def is_wontfix(self, key):
        return self.get_value(key) == ProgressStatus.WONTFIX

    # Write primitives

    def add_keys(self, keys):
        '''Add new keys with default value=INCOMPLETE'''
        try:
            old_keys = self.keys()
        except:
            old_keys = []

        # Remove keys that already exist, so we don't overwrite values
        keys = list(set(keys).difference(set(old_keys)))

        # Update with default value=INCOMPLETE
        persist.update_json_file(
            self.path,
            {k: ProgressStatus.INCOMPLETE for k in keys}
        )
        self.refresh_data()

    def mark_complete(self, key):
        '''Mark a key's value as complete.'''
        persist.update_json_file(self.path, {key: ProgressStatus.COMPLETE})
        logger.debug("%s - COMPLETE" % key)
        self.refresh_data()

    def mark_wontfix(self, key):
        '''Mark a key as wontfix so that we know not to try it again.'''
        persist.update_json_file(self.path, {key: ProgressStatus.WONTFIX})
        logger.debug("%s - WONTFIX" % key)
        self.refresh_data()

    def delete_key(self, key):
        '''Remove a key-value pair from the store.'''
        def del_fn(data, new_data):
            del data[key]
        persist.update_json_file(self.path, {}, update_fn=del_fn)
        logger.debug("%s - DELETED KEY")
        self.refresh_data()

    # Other write functions

    def destructive_reset(self, keys):
        '''Destroy savefile and recreate with new keys.'''
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass
        self.add_keys(keys)
