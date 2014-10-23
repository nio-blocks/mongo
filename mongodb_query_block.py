from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.string import StringProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.bool import BoolProperty
from nio.common.signal.base import Signal
import ast


@Discoverable(DiscoverableType.block)
class MongoDBQuery(Block):

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
    condition = ExpressionProperty(title='Condition', default="{'id': {'$gt': 0}}")
    limit = IntProperty(title='Limit', default=0)

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

    def process_signals(self, signals):
        output = []
        for s in signals:
            try:
                collection = self._evaluate_collection(s)
                condition = self._evaluate_condition(s)
                condition = self._check_condition(condition)
                output.extend(self._query_mongo(collection, condition))
            except:
                continue
        if output:
            self.notify_signals(output)

    def _connect_to_db(self):
        import pymongo
        self._client = pymongo.MongoClient(self.host, self.port)
        self._db = getattr(self._client, self.database)
        if self.username:
            self._db.authenticate(self.username, self.password, source="admin")

    def _get_sub_collection(self, collection, collection_name):
        for c in collection_name.split('.'):
            collection = getattr(collection, c)
        return collection

    def _evaluate_collection(self, signal):
        try:
            collection_name = self.collection(signal)
            collection = self._get_sub_collection(self._db,
                                                    collection_name)
            return collection
        except Exception as e:
            self._logger.error("Collection failed to evaluate.")
            raise e

    def _evaluate_condition(self, signal):
        try:
            condition = self.condition(signal)
            return condition
        except Exception as e:
            self._logger.error("Condition failed to evaluate.")
            raise e

    def _check_condition(self, condition):
        if not condition:
            # if no condition is specified, then that is valid
            return None
        if not isinstance(condition, dict):
            try:
                condition = ast.literal_eval(condition)
            except Exception as e:
                self._logger.error("Condition needs to be a dict: "
                                    "{}".format(condition))
                raise e
        if not isinstance(condition, dict):
            self._logger.error("Condition needs to be a dict: "
                                "{}".format(condition))
            raise e
        return condition

    def _query_mongo(self, collection, condition):
        output = []
        try:
            cursor = collection.find(spec=condition, limit=self.limit)
            output.extend([Signal(c) for c in cursor])
        except Exception as e:
            self._logger.error(
                "Error querying mongo: {}: {}".format(
                    type(e).__name__, str(e)))
            raise e
        return output
