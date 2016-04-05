from ..mongodb_command_block import MongoDBCommand
from unittest.mock import MagicMock, patch
from nio.testing.block_test_case import NIOBlockTestCase
from nio.signal.base import Signal


class SignalA(Signal):

    def __init__(self, a):
        super().__init__()
        self.a = a


class TestMongoDBCommand(NIOBlockTestCase):

    # test_default, test_expression_prop and test_dict are all different
    # ways to run the same command
    @patch('pymongo.MongoClient')
    def test_default(self, mongo):
        blk = MongoDBCommand()
        self.configure_block(blk, {})
        signal = SignalA('dbstats')
        collection = MagicMock()
        blk._db.command = MagicMock()
        blk.execute_query(collection, signal)
        blk._db.command.assert_called_with('dbstats')

    @patch('pymongo.MongoClient')
    def test_expression_prop(self, mongo):
        blk = MongoDBCommand()
        self.configure_block(blk, {'command': '{{ $a }}'})
        signal = SignalA('dbstats')
        collection = MagicMock()
        blk._db.command = MagicMock()
        blk.execute_query(collection, signal)
        blk._db.command.assert_called_with('dbstats')

    @patch('pymongo.MongoClient')
    def test_dict(self, mongo):
        blk = MongoDBCommand()
        self.configure_block(blk, {'command': "{'dbStats': 1}"})
        signal = SignalA('dbstats')
        collection = MagicMock()
        blk._db.command = MagicMock()
        blk.execute_query(collection, signal)
        blk._db.command.assert_called_with({'dbStats': 1})
