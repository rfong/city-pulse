import tempfile
import unittest

from yelp.progress import ProgressMeter
from yelp.progress import ProgressStatus


def get_nonexistent_tmp_file_name():
    f = tempfile.NamedTemporaryFile()
    fname = f.name
    f.close()  # File is auto deleted
    return fname

class TestProgressMeter(unittest.TestCase):

    def test_reset(self):
        meter = ProgressMeter(path=get_nonexistent_tmp_file_name())
        self.assertEqual(meter.get_data(), {})
        keys = ['foo', 'bar']
        meter.destructive_reset(keys)
        self.assertEqual(
            meter.get_data(),
            {
                'foo': ProgressStatus.INCOMPLETE,
                'bar': ProgressStatus.INCOMPLETE,
            }
        )
        self.assertEqual(set(meter.keys()), set(keys))

    def test_basic_functions(self):
        meter = ProgressMeter(path=get_nonexistent_tmp_file_name())
        # Should init with empty data
        self.assertEqual(meter.get_data(), {})
        # Mark complete
        self.assertEqual(meter.get_value('foo'), None)
        meter.mark_complete('foo')
        self.assertEqual(meter.get_value('foo'), ProgressStatus.COMPLETE)
        # Mark wontfix
        meter.mark_wontfix('foo')
        self.assertEqual(meter.get_value('foo'), ProgressStatus.WONTFIX)
        # Delete a key
        meter.delete_key('foo')
        self.assertEqual(meter.get_value('foo'), None)
        # Add keys
        meter.add_keys(['a', 'b'])
        self.assertEqual(meter.get_value('a'), ProgressStatus.INCOMPLETE)
        self.assertEqual(meter.get_value('b'), ProgressStatus.INCOMPLETE)
        # Adding keys shouldn't overwrite existing values
        meter.mark_complete('a')
        meter.mark_wontfix('c')
        meter.add_keys(['a', 'c', 'd'])
        self.assertEqual(meter.get_value('a'), ProgressStatus.COMPLETE)
        self.assertEqual(meter.get_value('c'), ProgressStatus.WONTFIX)
        self.assertEqual(meter.get_value('d'), ProgressStatus.INCOMPLETE)


if __name__ == '__main__':
    unittest.main()
