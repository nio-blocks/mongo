from .mongodb_base import MongoDBBase
from nio.util.discovery import discoverable
from nio.properties import Property, ListProperty, \
    PropertyHolder


class AggregationPipe(PropertyHolder):
    pipe = Property(
        title="Pipe Expression",
        default="{'$group': {'_id': '$field', 'count': {'$sum': 1}}}")


@discoverable
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
        for pipe in self.pipeline():
            pipes.append(self.evaluate_expression(pipe.pipe, signal))

        self.logger.debug("Searching aggregation {}".format(pipes))

        cursor = collection.aggregate(pipes, **(self.query_args()))
        return [cursor]
