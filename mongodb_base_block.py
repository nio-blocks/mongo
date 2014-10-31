from nio.common.block.base import Block
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.object import ObjectProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.holder import PropertyHolder


class Credentials(PropertyHolder):
    """ User credentials
    Properties:
        username (str): User to connect as
        password (str): User's password
    """
    username = StringProperty(title='User to connect as')
    password = StringProperty(title='Password to connect with')


class MongoDBBase(Block):
    """ A block for querying a mongodb.

    Properties:
        host (str): location of the database
        port (int): open port served by database
        database (str): database name
        collection (expression): collection name

    """
    host = StringProperty(title='Mongo Host', default="127.0.0.1")
    port = IntProperty(title='Port', default=27017)
    database = StringProperty(title='Database Name', default="test")
    collection = ExpressionProperty(title='Collection Name', default="signals")
    creds = ObjectProperty(Credentials, title='Credentials')

    def __init__(self):
        super().__init__()
        self._client = None
        self._db = None

    def configure(self, context):
        super().configure(context)
        try:
            self._connect_to_db()
        except Exception as e:
            self._logger.error(
                "Could not connect to Mongo instance: {}".format(e))

    def stop(self):
        if self._client:
            self._client.close()
        super().stop()

    def _connect_to_db(self):
        import pymongo
        self._client = pymongo.MongoClient(self.host, self.port)
        self._db = getattr(self._client, self.database)
        if self.creds.username:
            self._db.authenticate(self.creds.username,
                                  self.creds.password,
                                  source="admin")

    def _get_sub_collection(self, collection, collection_name):
        for col in collection_name.split('.'):
            collection = getattr(collection, col)
        return collection

    def _evaluate_collection(self, signal):
        """Blocks that use MongoDBBase should call _evaluate_collection
        to get the mongo collection. If this methed raises an exception,
        skip the signal.
        """
        try:
            collection_name = self.collection(signal)
            collection = self._get_sub_collection(self._db,
                                                  collection_name)
            return collection
        except Exception as e:
            self._logger.error("Collection failed to evaluate: {}".format(e))
            raise e
