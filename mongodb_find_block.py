from .mongodb_base_block import MongoDBBase, Limitable, Sortable
from nio.common.block.attribute import Output
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty, VersionProperty


@Output('no_results')
@Output('results')
@Discoverable(DiscoverableType.block)
class MongoDBFind(Limitable, Sortable, MongoDBBase):

    """ A block for running `find` against a mongodb.

    Properties:
        condition (expression): A dictionary form of a find expression. This is
        an expression property that can evaluate to a dictionary or be a
        parseable JSON string

    """
    condition = ExpressionProperty(
        title='Condition', default="{'id': {'$gt': 0}}")
    version = VersionProperty('2.0.0')

    def execute_query(self, collection, signal):
        condition = self.evaluate_expression(self.condition, signal)
        self._logger.debug("Searching condition {}".format(condition))

        if self.pymongo3():
            cursor = collection.find(filter=condition, **(self.query_args()))
        else:
            cursor = collection.find(spec=condition, **(self.query_args()))

        # If we got nothing, send an empty signal to the no results output
        if cursor.count() == 0:
            self.notify_output_signals({}, signal, output='no_results')

        return cursor

    def write_results(self, results):
        """ Notify the signals on the results output """
        if results:
            self.notify_signals(results, 'results')
