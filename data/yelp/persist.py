'''
Handle updates to local key-value store
'''

import json
import logging
import os
import sys
import tempfile

from . import util

logger = logging.getLogger(__name__)


def update_json_file(fname, new_data, update_fn=None, pretty_print=True):
    '''
    Update a JSON file with new data.
    If no `update_fn` function is provided, do a standard dictionary update.
    `fname` is an absolute path.
    Atomic file swap, so that if we crash, we will still have the old file.
    '''
    # If file already exists, read existing data.
    try:
        with open(fname, 'r') as f:
            data = json.loads(f.read()) or {}
    # If file does not exist yet, use a default empty value.
    except FileNotFoundError:
        logger.info('File %s does not exist yet. Instantiating.' % fname)
        data = {}
    # If file is not parseable, shout & abort.
    except json.decoder.JSONDecodeError:
        logger.error('File %s is not parseable as JSON.' % fname)
        raise
    except:
        logger.error('Unexpected error:', sys.exc_info()[0])
        return

    # Update:
    if update_fn is None:
        data.update(new_data)
    else:
        data = update_fn(data, new_data)

    # Print to file
    with open(tempfile.NamedTemporaryFile().name, 'w') as f:
        logger.debug('Writing new data to tempfile: %s' % f.name)
        if pretty_print:
            f.write(json.dumps(data, indent=4, separators=(',', ': ')))
        else:
            f.write(json.dumps(data))
        # Overwrite original file
        logger.debug(
            'Moving tempfile to overwrite original JSON file. %s' %
            json.dumps({
                'tempfile': f.name,
                'destination': fname,
            })
        )
        os.replace(f.name, fname)
