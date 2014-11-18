from unittest import skipIf
from nio.util.support.block_test_case import NIOBlockTestCase
from nio.common.signal.base import Signal
from ..mongodb_find_block import MongoDBFind
from ..mongodb_update_block import MongoDBUpdate
from ..mongo_insert_block import MongoDBInsert

pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = 'test'
MONGO_COLL = 'signals'

SIGNAL_VALUE = 'inserted by block'
UPDATED_SIGNAL_VALUE = 'updated by block'


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoCRUD(NIOBlockTestCase):

    """ Tests the CRUD operations on a MongoDB with all available blocks """

    def setUp(self):
        super().setUp()
        # Clear out the collection before we start
        self._clear_db()

    def tearDown(self):
        # Clear out the collection again, to be safe
        self._clear_db()
        super().tearDown()

    def _clear_db(self):
        collection = pymongo.MongoClient(
            MONGO_HOST, MONGO_PORT)[MONGO_DB][MONGO_COLL]
        collection.drop()

    def test_crud(self):
        self.insert_signal()  # C
        self.find_signal()    # R
        self.update_signal()  # U
        self.delete_signal()  # D

    def insert_signal(self):
        inserter = MongoDBInsert()
        self.configure_block(inserter, self._get_conf({
            "name": "Inserter"
        }))
        inserter.start()
        inserter.process_signals([Signal({'val': SIGNAL_VALUE})])
        inserter.stop()

    def find_signal(self):
        finder = MongoDBFind()
        self.configure_block(finder, self._get_conf({
            "condition": "{'val': '" + SIGNAL_VALUE + "'}",
            "name": "ReadFind"
        }))
        finder.start()
        finder.process_signals([Signal()])
        self.assert_num_signals_notified(1, finder)
        finder.stop()

    def update_signal(self):
        updater = MongoDBUpdate()
        self.configure_block(updater, self._get_conf({
            "spec": "{'val': '" + SIGNAL_VALUE + "'}",
            "document": "{'val': '" + UPDATED_SIGNAL_VALUE + "'}",
            "name": "Updater"
        }))

        # Should find the updated value
        finder = MongoDBFind()
        self.configure_block(finder, self._get_conf({
            "condition": "{'val': '" + UPDATED_SIGNAL_VALUE + "'}",
            "name": "UpdaterFind"
        }))

        # Should not find the original value
        dont_finder = MongoDBFind()
        self.configure_block(dont_finder, self._get_conf({
            "condition": "{'val': '" + SIGNAL_VALUE + "'}",
            "name": "UpdaterDontFind"
        }))

        updater.start()
        finder.start()
        dont_finder.start()

        # Trigger the blocks to work
        updater.process_signals([Signal()])
        finder.process_signals([Signal()])
        dont_finder.process_signals([Signal()])

        self.assert_num_signals_notified(1, finder)
        self.assert_num_signals_notified(0, dont_finder)

        dont_finder.stop()
        finder.stop()
        updater.stop()

    def delete_signal(self):
        # TODO: Add a MongoDelete block
        pass

    def _get_conf(self, conf):
        """ Return the passed conf, merged with the server conf"""
        mongo_conf = {
            'host': MONGO_HOST,
            'port': MONGO_PORT,
            'database': MONGO_DB,
            'collection': MONGO_COLL,
            'log_level': 'DEBUG'
        }
        return dict(list(mongo_conf.items()) + list(conf.items()))
