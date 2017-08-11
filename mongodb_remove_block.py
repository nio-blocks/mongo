from nio.properties import Property, BoolProperty

from .mongodb_base import MongoDBBase


class MongoDBRemove(MongoDBBase):

    """ A block for running `remove` against a mongodb.

    Properties:
        condition (expression): A dictionary form of a remove expression. This
        is an expression property that can evaluate to a dictionary or be a
        parseable JSON string

    """
    condition = Property(
        title='Condition',
        default="{'id': {'$gt': 0}}")
    only_one = BoolProperty(
        title='Maximum One Deletion',
        default=False)

    def execute_query(self, collection, signal):
        condition = self.evaluate_expression(self.condition, signal)
        self.logger.debug("Deleting on condition {}".format(condition))

        res = collection.remove(condition, multi=(not self.only_one()))
        return [{'deleted': res.get('n', 0)}]
