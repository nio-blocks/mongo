from .mongo_block import MongoDB
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.string import StringProperty


@Discoverable(DiscoverableType.block)
class MongoBulkInsert(MongoDB):

    """ The same as the Mongo Block except that it won't evaluate the
    collection property on each signal. It will also save signals as a list
    of signals, rather than one-by-one.

    Use this block for better performance on large volume inserts.
    """
    collection = StringProperty(title='Collection Name', default="signals")

    def _connect_to_db(self):
        super()._connect_to_db()
        if self._db:
            self._collection = self._get_sub_collection(self._db, self.collection)
        else:
            self._collection = None

    def process_signals(self, signals):
        try:
            self._save(self._collection, signals)
        except Exception as e:
            self._logger.error(
                "Collection name evaluation failed: {0}: {1}".format(
                    type(e).__name__, str(e))
            )

    def _save(self, collection, signals):
        try:
            collection.insert(self._bulk_generator(signals))
        except Exception as e:
            self._logger.error("Could not record signal: %s" % e)

    def _bulk_generator(self, signals):
        for s in signals:
            yield s.to_dict(self.with_type)
