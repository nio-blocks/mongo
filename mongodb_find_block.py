from .mongodb_base_block import MongoDBBase, Limitable, Sortable
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.common.signal.base import Signal


@Discoverable(DiscoverableType.block)
class MongoDBFind(Limitable, Sortable, MongoDBBase):

    """ A block for running `find` against a mongodb.

    Properties:
        condition (expression): A dictionary form of a find expression. This is
        an expression property that can evaluate to a dictionary or be a
        parseable JSON string

    """
    condition = ExpressionProperty(
        title='Condition',
        default="{'id': {'$gt': 0}}")

    def execute_query(self, collection, signal):
        condition = self.evaluate_expression(self.condition, signal)
        self._logger.debug("Searching condition {}".format(condition))

        cursor = collection.find(spec=condition, **(self.query_args()))
        return [Signal(c) for c in cursor]
