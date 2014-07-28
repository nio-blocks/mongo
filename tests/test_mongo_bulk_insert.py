
pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

from ..mongo_bulk_insert import MongoBulkInsert
from unittest import skipIf
from unittest.mock import MagicMock, patch, ANY
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


class SignalA(Signal):
    def __init__(self, a):
        super().__init__()
        self.a = a


class SignalAB(Signal):
    def __init__(self, a, b):
        super().__init__()
        self.a = a
        self.b = b


class SignalBCD(Signal):
    def __init__(self, b, c, d):
        super().__init__()
        self.b = b
        self.c = c
        self.d = d


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoBulkInsert(NIOBlockTestCase):
    @patch('pymongo.MongoClient')
    def test_aggregation(self, mongo):
        blk = MongoBulkInsert()
        blk._save = MagicMock()
        self.configure_block(blk, {'with_type': True})
        signals = [
            SignalA('foo'),
            SignalA('bar'),
            SignalA('baz'),
            SignalA('qux')
        ]
        blk.start()
        blk.process_signals(signals)
        blk._save.assert_called_once_with(
            blk._db.signals, signals
        )
        blk.stop()

    def test_save_to_db(self):
        blk = MongoBulkInsert()
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
        blk = MongoBulkInsert()
        with self.assertRaises(Exception):
            self.configure_block(blk, {
                'host': "some_bogus_host",
                'port': 8080
            })
