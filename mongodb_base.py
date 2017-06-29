import ast
import ssl
from enum import Enum
from nio.block.base import Block
from nio.block.mixins.enrich.enrich_signals import EnrichSignals
from nio.properties import Property, StringProperty, \
    ObjectProperty, IntProperty, PropertyHolder, ListProperty, \
    SelectProperty, VersionProperty, BoolProperty

__all__ = ['MongoDBBase', 'Limitable', 'Sortable']


class Connection(PropertyHolder):

    """ Mongo connection properties
    Properties:
        host (str): Database host
        port (int): Database port
        ssl (bool): Whether or not to use SSL when connecting
                    (certs won't be validated)
    """
    host = StringProperty(title='Mongo Host', default="127.0.0.1")
    port = IntProperty(title='Port', default=27017)
    ssl = BoolProperty(title='Use SSL', default=False)


class Credentials(PropertyHolder):

    """ User credentials
    Properties:
        username (str): User to connect as
        password (str): User's password
    """
    username = StringProperty(title='User to connect as', default="")
    password = StringProperty(title='Password to connect with', default="")


class Limitable():

    """ A Mongo block mixin that allows you to limit results """

    limit = IntProperty(title='Limit', default=0)

    def query_args(self):
        existing_args = super().query_args()
        existing_args['limit'] = self.limit()
        return existing_args


class SortDirection(Enum):
    DESCENDING = -1
    ASCENDING = 1


class Sort(PropertyHolder):
    key = StringProperty(title="Key", default="key")
    direction = SelectProperty(SortDirection,
                               default=SortDirection.ASCENDING,
                               title="Direction")


class Sortable():

    """ A Mongo block mixin that allows you to sort results """

    sort = ListProperty(Sort, title='Sort', default=[])

    def __init__(self):
        super().__init__()
        self._sort = []

    def configure(self, context):
        super().configure(context)

        self._sort = [(s.key(), s.direction().value) for s in self.sort()]

    def query_args(self):
        existing_args = super().query_args()
        existing_args['sort'] = self._sort
        return existing_args


class MongoDBBase(EnrichSignals, Block):

    """ A block for querying a mongodb.  """

    connection = ObjectProperty(
        Connection, title='Connection', default=Connection())
    database = StringProperty(title='Database Name', default="test")
    collection = Property(title='Collection Name', default="signals")
    creds = ObjectProperty(
        Credentials, title='Credentials', default=Credentials())
    version = VersionProperty('3.0.0')

    def __init__(self):
        super().__init__()
        self._client = None
        self._db = None

    def configure(self, context):
        super().configure(context)
        try:
            self._connect_to_db()
            self.logger.debug("Connected")
        except Exception as e:
            self.logger.error(
                "Could not connect to Mongo instance: {}".format(e))

    def stop(self):
        if self._client:
            self._client.close()
        super().stop()

    def pymongo3(self):
        """ Returns True if the version of pymongo is 3 or greater """
        import pymongo
        pymongo_major_version = int(pymongo.version.split('.')[0])
        return pymongo_major_version >= 3

    def process_signals(self, signals):
        output = []
        for s in signals:
            coll = self._evaluate_collection(s)
            self.logger.debug("Evaluating in collection {}".format(coll))
            if coll:
                try:
                    results = self.execute_query(coll, s)
                    output.extend([self.get_output_signal(result, s)
                                   for result in results])
                except:
                    # If the execute call fails, we won't use this signal
                    self.logger.exception("Query failed")

        self.write_results(output)

    def write_results(self, results):
        """ Notify results as a list of signals.

        This can be overridden to notify on different outputs.
        """
        if results:
            self.notify_signals(results)

    def query_args(self):
        """ Query arguments to use in the pymongo query.

        Returns:
            args (dict): A dictionary of kwargs to pass to pymongo queries
        """
        return {}

    def execute_query(self, collection, signal):
        """ Run this block's query on the provided collection.

        This should be overriden in the child blocks. It will be passed
        a valid pymongo collection against which it can query.

        If the block wishes, it may return a list of signals that will be
        notified.

        Params:
            collection (pymongo.Collection): A valid collection
            signal (Signal): The signal which triggered the query

        Returns:
            signals (list): A list of signal dicts to notify
        """
        raise NotImplementedError()

    def evaluate_expression(self, expression, signal, force_dict=True):
        """ Evaluates an expression against a signal.

        This method will allow the expression to evaluate to a dictionary or
        a string representing a dictionary. In either case, a dictionary will
        be returned. If both of those fail, the value of force_dict determines
        whether or not the expression can be returned.

        Params:
            expression (expression): The Property reference
            signal (Signal): The signal to use to evaluate the expression
            force_dict (bool): Whether or not the expression has to evaluate
                to a dictionary

        Returns:
            result: The result of the expression evaluated with the signal

        Raises:
            TypeError: If force_dict is True and the expression is not a dict
        """
        exp_result = expression(signal)
        if not isinstance(exp_result, dict):
            try:
                # Let's at least try to make it a dict first
                exp_result = ast.literal_eval(exp_result)
            except:
                # Didn't work, this may or may not be a problem, we'll find out
                # in the next block of code
                pass

        if not isinstance(exp_result, dict):
            # Ok, this is still not a dict, what should we do?
            if force_dict:
                raise TypeError(" needs to eval to a dict: "
                                "{}".format(expression))

        return exp_result

    def _connect_to_db(self):
        import pymongo
        self._client = pymongo.MongoClient(
            self.connection().host(),
            self.connection().port(),
            ssl=self.connection().ssl(),
            ssl_cert_reqs=ssl.CERT_NONE  # currently no support for validation
        )
        self._db = getattr(self._client, self.database())
        if self.creds().username():
            self.logger.debug("Using authentication in login")
            self._db.authenticate(self.creds().username(),
                                  self.creds().password())

    def _get_sub_collection(self, collection, collection_name):
        for col in collection_name.split('.'):
            collection = collection[col]
        return collection

    def _evaluate_collection(self, signal):
        """ Returns the collection this block has been configured to query.

        If the collection is invalid or does not exist, this will return None
        """
        try:
            collection_name = self.collection(signal)
            collection = self._get_sub_collection(self._db,
                                                  collection_name)
            return collection
        except Exception as e:
            self.logger.error("Collection failed to evaluate: {}".format(e))
