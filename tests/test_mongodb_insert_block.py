from unittest import skipIf
from unittest.mock import MagicMock, patch

from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal

from ..mongodb_insert_block import MongoDBInsert

pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoDB(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_aggregation(self, mock_client):
        blk = MongoDBInsert()
        blk.execute_query = MagicMock()
        self.configure_block(blk, {'with_type': True})
        signals = [
            SignalA('foo')
        ]
        blk.start()
        blk.process_signals(signals)
        blk.execute_query.assert_called_once_with(
            blk._db['signals'], signals[0]
        )
        blk.stop()

    @patch('pymongo.MongoClient')
    def test_save_to_db(self, mock_client):
        blk = MongoDBInsert()
        self.configure_block(blk, {'with_type': True})
        signals = [
            SignalA('foo')
        ]
        collection = pymongo.MongoClient('127.0.0.1', 27017).test.signals
        collection.drop()
        blk.start()
        blk.process_signals(signals)
        for obj in collection.find():
            obj = {key: obj[key] for key in obj if key != '_id'}
            self.assertEqual(obj, signals[0].to_dict(with_type=True))
        blk.stop()

    @patch('pymongo.MongoClient')
    @patch.object(MongoDBInsert, "execute_query")
    def test_collection_expr_fail(self, mock_save, mock_client):
        """ Make sure a bad collection causes no query to run """

        blk = MongoDBInsert()
        self.configure_block(blk, {
            "collection": "{{dict($foo)}}"
        })
        signals = [Signal({'foo': 'bar'})]

        blk.start()
        blk.process_signals(signals)
        self.assertFalse(mock_save.called)

        blk.stop()

    @patch('pymongo.MongoClient')
    def test_bad_naming(self, mock_client):
        blk = MongoDBInsert()
        # count is a mongo function.
        self.configure_block(blk, {'collection': 'count'})
        signals = [
            SignalA('foo')
        ]
        collection = mock_client('127.0.0.1', 27017).test['count']
        collection.drop()
        blk.start()
        blk.process_signals(signals)
        for obj in collection.find():
            obj = {key: obj[key] for key in obj if key not in {'_id', '_type'}}
            self.assertEqual(obj, signals[0].to_dict(with_type=False))
        blk.stop()
