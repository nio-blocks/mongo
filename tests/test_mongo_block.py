
pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

from ..mongo_block import MongoDB
from unittest import skipIf
from unittest.mock import MagicMock, patch, ANY
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoDB(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_aggregation(self, mongo):
        blk = MongoDB()
        blk._save = MagicMock()
        self.configure_block(blk, {'with_type': True})
        signals = [
            SignalA('foo')
        ]
        blk.start()
        blk.process_signals(signals)
        blk._save.assert_called_once_with(
            blk._db.signals, signals[0]
        )
        blk.stop()

    def test_save_to_db(self):
        blk = MongoDB()
        try:
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
        except AssertionError as e:
            raise e
        except Exception as e:
            pass

    def test_connection_failure(self):
        blk = MongoDB()
        blk._logger.error = MagicMock()
        self.configure_block(blk, {
            'host': "some_bogus_host",
            'port': 8080
        })
        with self.assertRaises(Exception):
            blk._connect_to_db()

    @patch('pymongo.MongoClient')
    @patch("mongo.mongo_block.MongoDB._save")
    def test_collection_expr_fail(self, mock_save, mock_client):
        blk = MongoDB()
        self.configure_block(blk, {
            "collection": "{{dict($foo)}}"
        })
        signals = [Signal({'foo': 'bar'})]

        blk.start()
        blk.process_signals(signals)
        with self.assertRaises(AssertionError):
            mock_save.assert_called_with(ANY, ANY)

        blk.stop()
