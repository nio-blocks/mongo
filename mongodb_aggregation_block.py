from nio.properties import Property, ListProperty, \
    PropertyHolder

from .mongodb_base import MongoDBBase


class AggregationPipe(PropertyHolder):
    pipe = Property(
        title="Pipe Expression",
        default="{'$group': {'_id': '$field', 'count': {'$sum': 1}}}")


class MongoDBAggregation(MongoDBBase):

    """ A block for finding and grouping multiple documents together."""
    pipeline = ListProperty(AggregationPipe,
                            title="Aggregation Pipeline",
                            default=[AggregationPipe()])

    def execute_query(self, collection, signal):
        pipes = []
        for pipe in self.pipeline():
            pipes.append(self.evaluate_expression(pipe.pipe, signal))

        self.logger.debug("Searching aggregation {}".format(pipes))

        cursor = collection.aggregate(pipes, **(self.query_args()))
        return cursor
