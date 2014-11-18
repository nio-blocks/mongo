from nio.common.signal.base import Signal
from ..mongodb_find_block import MongoDBFind
from ..mongodb_update_block import MongoDBUpdate
from ..mongo_insert_block import MongoDBInsert
from .test_mongo_base import TestMongoBase

SIGNAL_VALUE = 'inserted by block'
UPDATED_SIGNAL_VALUE = 'updated by block'


class TestMongoCRUD(TestMongoBase):

    """ Tests the CRUD operations on a MongoDB with all available blocks """

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
