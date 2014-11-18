from .mongodb_base_block import MongoDBBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty, ListProperty, \
    PropertyHolder
from nio.common.signal.base import Signal


class AggregationPipe(PropertyHolder):
    pipe = ExpressionProperty(title="Pipe Expression",
                              default="{'$group': {'_id': '$field', " +
                                      "'count': {'$sum': 1}}}")


@Discoverable(DiscoverableType.block)
class MongoDBAggregation(MongoDBBase):

    """ A block for running `find` against a mongodb.

    Properties:
        condition (expression): A dictionary form of a find expression. This is
        an expression property that can evaluate to a dictionary or be a
        parseable JSON string

    """
    pipeline = ListProperty(AggregationPipe, title="Aggregation Pipeline")

    def execute_query(self, collection, signal):
        pipes = []
        for pipe in self.pipeline:
            pipes.append(self.evaluate_expression(pipe.pipe, signal))

        self._logger.debug("Searching aggregation {}".format(pipes))

        cursor = collection.aggregate(pipes, **(self.query_args()))
        return [Signal(cursor)]
