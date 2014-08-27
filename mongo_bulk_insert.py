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

    def process_signals(self, signals):
        try:
            collection = getattr(self._db, self.collection)
            self._save(collection, signals)
        except Exception as e:
            self._logger.error(
                "Collection name evaluation failed: {0}: {1}".format(
                    type(e).__name__, str(e))
            )

    def _save(self, collection, signals):
        try:
            signals = [s.to_dict(self.with_type) for s in signals]
            collection.insert(signals)
        except Exception as e:
            self._logger.error("Could not record signal: %s" % e)
