import os

def localize_path(path):
    '''Make path relative to current module'''
    return os.path.join(os.path.dirname(__file__), path)

