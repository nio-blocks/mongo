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
    host = StringProperty(title='Mongo Host', default="127.0.0.1")
    port = IntProperty(title='Port', default=27017)
    database = StringProperty(title='Database Name', default="test")
    collection = ExpressionProperty(title='Collection Name', default="signals")
    with_type = BoolProperty(
        title='Include the type of logged signals?', default=False)

    username = StringProperty(title='User to connect as')
    password = StringProperty(title='Password to connect with')

    def __init__(self):
        super().__init__()
        self._client = None
        self._db = None

    def configure(self, context):
        super().configure(context)
        try:
            self._connect_to_db()
        except Exception as e:
            self._logger.error("Could not connect to Mongo instance: %s" % e)

    def stop(self):
        if self._client:
            self._client.close()
        super().stop()

    def _connect_to_db(self):
        import pymongo
        self._client = pymongo.MongoClient(self.host, self.port)

        self._db = getattr(self._client, self.database)

        if self.username:
            self._db.authenticate(self.username, self.password, source="admin")

    def _get_sub_collection(self, collection, collection_name):
        for c in collection_name.split('.'):
            collection = collection[c]
        return collection

    def process_signals(self, signals):
        for s in signals:
            try:
                collection_name = self.collection(s)
                collection = self._get_sub_collection(self._db, collection_name)
                self._save(collection, s)
            except Exception as e:
                self._logger.error(
                    "Error saving signal: {0}: {1}".format(
                        type(e).__name__, str(e)))

    def _save(self, collection, signal):
        collection.save(signal.to_dict(self.with_type))
