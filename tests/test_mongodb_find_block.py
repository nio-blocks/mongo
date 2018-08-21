from unittest import skipIf
from unittest.mock import MagicMock, patch
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from ..mongodb_find_block import MongoDBFind


pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoDB(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_find(self, mock_client):
        mock_results = [{'a': 1}, {'b': 2}]
        mock_collection = MagicMock()
        mock_cursor = mock_collection.find.return_value = MagicMock()
        mock_cursor.count.return_value = 2
        # we're going to iterate over this mock generator to get our results
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_results))
        blk = MongoDBFind()
        # mock this method, returns a collection which we also mock
        blk._evaluate_collection = MagicMock(return_value=mock_collection)
        self.configure_block(blk, {})
        signals = [Signal()]
        blk.start()
        blk.process_signals(signals)
        blk.stop()
        self.assertEqual(len(self.last_notified['results']), 2)
        self.assertDictEqual(
            self.last_notified['results'][0].to_dict(), mock_results[0])
        self.assertDictEqual(
            self.last_notified['results'][1].to_dict(), mock_results[1])

    @patch('pymongo.MongoClient')
    def test_no_results(self, mock_client):
        mock_results = []
        mock_collection = MagicMock()
        mock_cursor = mock_collection.find.return_value = MagicMock()
        mock_cursor.count.return_value = 0
        # we're going to iterate over this mock generator to get our results
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_results))
        blk = MongoDBFind()
        # mock this method, returns a collection which we also mock
        blk._evaluate_collection = MagicMock(return_value=mock_collection)
        self.configure_block(blk, {'enrich': {'exclude_existing': False}})
        signals = [Signal({'pi': 3.14})]
        blk.start()
        blk.process_signals(signals)
        blk.stop()
        self.assertEqual(len(self.last_notified['no_results']), 1)
        self.assertDictEqual(
            self.last_notified['no_results'][0].to_dict(), {'pi': 3.14})
