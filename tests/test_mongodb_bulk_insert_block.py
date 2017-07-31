from ..mongodb_bulk_insert_block import MongoDBBulkInsert, DuplicateKeyError
from unittest.mock import MagicMock, patch
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


class TestMongoBulkInsert(NIOBlockTestCase):

    @patch('pymongo.MongoClient')
    def test_bulk_aggregation(self, mongo):
        blk = MongoDBBulkInsert()
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
        self.assertEqual(blk._collection.insert.call_count, 1)
        self.assertEqual(blk._collection.insert.call_args[1],
                         {'continue_on_error': True})
        blk.stop()

    @patch('pymongo.MongoClient')
    def test_duplicate_key_error(self, mongo):
        blk = MongoDBBulkInsert()
        self.configure_block(blk, {'with_type': True})
        blk._collection.insert = MagicMock()
        blk._collection.insert.side_effect = DuplicateKeyError('uh oh')
        blk.logger.warning = MagicMock()
        signals = [
            SignalA('foo')
        ]
        blk.start()
        blk.process_signals(signals)
        self.assertEqual(blk._collection.insert.call_count, 1)
        blk.logger.warning.assert_called_with('DuplicateKeyError: uh oh')
        blk.stop()

    @patch('pymongo.MongoClient')
    def test_error(self, mongo):
        blk = MongoDBBulkInsert()
        self.configure_block(blk, {'with_type': True})
        blk._collection.insert = MagicMock()
        blk._collection.insert.side_effect = Exception('uh oh')
        blk.logger.error = MagicMock()
        signals = [
            SignalA('foo')
        ]
        blk.start()
        blk.process_signals(signals)
        self.assertEqual(blk._collection.insert.call_count, 1)
        blk.logger.error.assert_called_with('Collection insert failed:'
                                             ' Exception: uh oh')
        blk.stop()
