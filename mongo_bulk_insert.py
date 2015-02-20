from .mongo_insert_block import MongoDBInsert
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.string import StringProperty
from pymongo.errors import DuplicateKeyError


@Discoverable(DiscoverableType.block)
class MongoBulkInsert(MongoDBInsert):

    """ The same as the Mongo Block except that it won't evaluate the
    collection property on each signal. It will also save signals as a list
    of signals, rather than one-by-one.

    Use this block for better performance on large volume inserts.
    """
    collection = StringProperty(title='Collection Name', default="signals")

    def configure(self, context):
        super().configure(context)

        # After super configuring (this will connect, we can get our collection
        if self._db:
            self._collection = self._get_sub_collection(
                self._db, self.collection)
        else:
            self._collection = None

    def process_signals(self, signals):
        try:
            self._logger.debug("Inserting {} signals".format(len(signals)))
            self._collection.insert(
                [s.to_dict(self.with_type) for s in signals],
                continue_on_error=True
            )
        except DuplicateKeyError as e:
            self._logger.warning('{}: {}'.format(type(e).__name__, e))
        except Exception as e:
            self._logger.error(
                "Collection insert failed: {0}: {1}".format(
                    type(e).__name__, e))

    def _bulk_generator(self, signals):
        for s in signals:
            yield s.to_dict(self.with_type)
