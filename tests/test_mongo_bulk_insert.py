
pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

from ..mongo_bulk_insert import MongoBulkInsert
from unittest import skipIf
from unittest.mock import MagicMock, patch
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoBulkInsert(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_bulk_aggregation(self, mongo):
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
