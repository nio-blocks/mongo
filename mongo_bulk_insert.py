from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.bool import BoolProperty


@Discoverable(DiscoverableType.block)
class MongoBulkInsert(Block):

    """ A block for recording signals to a database or other such
    system-external store. This implementation is currently specific
    to MongoDB but will be generalized later.

    Properties:
        host (str): location of the database
        port (int): open port served by database
        database (str): database name
        collection (str): collection name
        with_type (str): include the signal type in the record?

    """
    host = StringProperty(title='Mongo Host', default="127.0.0.1")
    port = IntProperty(title='Port', default=27017)
    database = StringProperty(title='Database Name', default="test")
    collection = StringProperty(title='Collection Name', default="signals")
    with_type = BoolProperty(
        title='Include the type of logged signals?', default=False)

    def __init__(self):
        super().__init__()
        self._client = None
        self._db = None

    def configure(self, context):
        super().configure(context)
        try:
            import pymongo
            self._client = pymongo.MongoClient(self.host, self.port)
            self._db = getattr(self._client, self.database)
        except Exception as e:
            self._logger.error(
                "Could not connect to Mongo instance: %s" % e
            )
            raise e

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
            collection.save(signals)
        except Exception as e:
            self._logger.error("Could not record signal: %s" % e)
