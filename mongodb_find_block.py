from .mongodb_base import MongoDBBase, Limitable, Sortable
from nio.signal.base import Signal
from nio.block.terminals import output
from nio.util.discovery import discoverable
from nio.properties import Property, VersionProperty


@output('no_results')
@output('results')
@discoverable
class MongoDBFind(Limitable, Sortable, MongoDBBase):

    """ A block for running `find` against a mongodb.

    Properties:
        condition (expression): A dictionary form of a find expression. This is
        an expression property that can evaluate to a dictionary or be a
        parseable JSON string

    """
    condition = Property(
        title='Condition', default="{'id': {'$gt': 0}}")
    version = VersionProperty('2.0.0')

    def execute_query(self, collection, signal):
        condition = self.evaluate_expression(self.condition, signal)
        self.logger.debug("Searching condition {}".format(condition))

        if self.pymongo3():
            cursor = collection.find(filter=condition, **(self.query_args()))
        else:
            cursor = collection.find(spec=condition, **(self.query_args()))

        if cursor.count() == 0:
            self.notify_signals([signal], 'no_results')

        return cursor

    def write_results(self, results):
        """ Notify the signals on the results output """
        if results:
            self.notify_signals(results, 'results')
