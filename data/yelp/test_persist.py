import json
import os
import tempfile
import unittest

from yelp.persist import update_json_file


def get_nonexistent_tmp_file_name():
    f = tempfile.NamedTemporaryFile()
    fname = f.name
    f.close()  # File is auto deleted
    return fname


class TestPersist(unittest.TestCase):

    @staticmethod
    def my_update_fn(old_data, new_data):
        '''Updates old_data with new_data along the 'id' field'''
        for datum in new_data:
            old_data[datum.get('id')] = datum
        return old_data

    def test_update_file(self):
        '''Basic file update'''
        fname = get_nonexistent_tmp_file_name()
        data = {'foo': 'bar'}

        # Updating a nonexistent file should work fine; treat as empty data.
        update_json_file(fname, data)
        with open(fname, 'r') as f:
            read_data = json.loads(f.read())
            self.assertEqual(read_data, data)

        update_json_file(fname, {'two': 'bar2'})
        data['two'] = 'bar2'
        with open(fname, 'r') as f:
            read_data = json.loads(f.read())
            self.assertEqual(read_data, data)

    def test_custom_update_file(self):
        '''Update a file using a custom merging function'''
        fname = get_nonexistent_tmp_file_name()
        obj1 = {'id': '1', 'name': 'name1'}
        obj2 = {'id': '2', 'name': 'name2'}

        update_json_file(fname, [obj1, obj2],
                         update_fn=TestPersist.my_update_fn)
        with open(fname, 'r') as f:
            # File should have been created and contain data
            read_data = json.loads(f.read())
            self.assertEqual(read_data, {'1': obj1, '2': obj2})

        # Change obj1
        obj1['name'] = 'new_name1'
        update_json_file(fname, [obj1], update_fn=TestPersist.my_update_fn)
        with open(fname, 'r') as f:
            read_data = json.loads(f.read())
            self.assertEqual(read_data, {'1': obj1, '2': obj2})

    def test_update_empty_file(self):
        '''Using an existing empty file should raise a JSON parse error.'''
        f = tempfile.NamedTemporaryFile(delete=False)
        fname = f.name
        f.close()

        with self.assertRaises(json.decoder.JSONDecodeError):
            update_json_file(fname, {'foo': 'bar'})
        os.remove(fname)

    def test_custom_update_empty_file(self):
        '''Same as above, with custom update function.'''
        f = tempfile.NamedTemporaryFile(delete=False)
        fname = f.name
        f.close()

        obj = {'id': '1', 'name': 'name1'}
        with self.assertRaises(json.decoder.JSONDecodeError):
            update_json_file(fname, [obj], update_fn=TestPersist.my_update_fn)
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
