from ..mongo_bulk_insert import MongoBulkInsert
from unittest.mock import MagicMock, patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


class TestMongoBulkInsert(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_bulk_aggregation(self, mongo):
        blk = MongoBulkInsert()
        self.configure_block(blk, {'with_type': True})
        blk._collection.insert = MagicMock()
        signals = [
            SignalA('foo'),
            SignalA('bar'),
            SignalA('baz'),
            SignalA('qux')
        ]
        blk.start()
        blk.process_signals(signals)
        blk._collection.insert.assert_called_once()
        blk.stop()
