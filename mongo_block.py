from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.bool import BoolProperty


@Discoverable(DiscoverableType.block)
class MongoDB(Block):

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
    host = StringProperty(default="127.0.0.1")
    port = IntProperty(default=27017)
    database = StringProperty(default="test")
    collection = ExpressionProperty(default="signals")
    with_type = BoolProperty(default=False)

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
        for s in signals:
            try:
                collection_name = self.collection(s)
                collection = getattr(self._db, collection_name)
                self._save(collection, s)
            except Exception as e:
                self._logger.error(
                    "Collection name evaluation failed: {0}: {1}".format(
                        type(e).__name__, str(e))
                )

    def _save(self, collection, signal):
        try:
            collection.save(signal.to_dict(self.with_type))
        except Exception as e:
            self._logger.error("Could not record signal: %s" % e)
