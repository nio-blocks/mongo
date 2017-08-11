from nio.block.terminals import DEFAULT_TERMINAL
from nio.signal.base import Signal

from ..mongodb_find_block import MongoDBFind
from ..mongodb_update_block import MongoDBUpdate
from ..mongodb_insert_block import MongoDBInsert
from ..mongodb_remove_block import MongoDBRemove
from .test_mongodb_base import TestMongoBase

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
        self.assert_num_signals_notified(1, finder, 'results')
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

        self.assert_num_signals_notified(1, finder, 'results')
        self.assert_num_signals_notified(0, dont_finder, 'results')

        dont_finder.stop()
        finder.stop()
        updater.stop()

    def delete_signal(self):
        # clear out the signals so far
        self.last_notified[DEFAULT_TERMINAL][:] = []
        remover = MongoDBRemove()
        # Since we've updated the signal, we shouldn't remove the original
        self.configure_block(remover, self._get_conf({
            "condition": "{'val': '" + SIGNAL_VALUE + "'}",
            "name": "Remover"
        }))
        remover.start()
        remover.process_signals([Signal()])
        self.assert_num_signals_notified(1, remover)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][0].deleted, 0)
        remover.stop()

        # Now let's try to delete the real value, make sure we get 1 deleted
        self.configure_block(remover, self._get_conf({
            "condition": "{'val': '" + UPDATED_SIGNAL_VALUE + "'}",
            "name": "Remover"
        }))
        remover.start()
        remover.process_signals([Signal()])
        self.assert_num_signals_notified(2, remover)
        self.assertEqual(self.last_notified[DEFAULT_TERMINAL][1].deleted, 1)
        remover.stop()
