from unittest import skipIf
from unittest.mock import MagicMock, patch
from nio.block.terminals import DEFAULT_TERMINAL
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal
from ..mongodb_aggregation_block import MongoDBAggregation


pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoDB(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_aggregation(self, mock_client):
        mock_collection = MagicMock()
        # two results sets because why not
        set_a = {'a': 1}
        set_b = {'b': 2}
        mock_collection.aggregate.return_value = [set_a, set_b]
        blk = MongoDBAggregation()
        # mock this method, returns a collection which we also mock
        blk._evaluate_collection = MagicMock(return_value=mock_collection)
        self.configure_block(blk, {})
        signals = [Signal()]
        blk.start()
        blk.process_signals(signals)
        blk.stop()
        mock_collection.aggregate.assert_called_once_with([{'$group': {'_id': '$field', 'count': {'$sum': 1}}}])
        # one signal for each aggregated set
        self.assertEqual(2, len(self.last_notified[DEFAULT_TERMINAL]))
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][0].to_dict(),
            set_a)
        self.assertDictEqual(
            self.last_notified[DEFAULT_TERMINAL][1].to_dict(),
            set_b)
