from nio.properties.bool import BoolProperty

from .mongodb_base import MongoDBBase


class MongoDBInsert(MongoDBBase):

    """ A block for recording signals to a database or other such
    system-external store. This implementation is currently specific
    to MongoDB but will be generalized later.

    Properties:
        with_type (str): include the signal type in the record?

    """
    with_type = BoolProperty(
        title='Include the type of logged signals?', default=False)

    def execute_query(self, collection, signal):
        id = collection.save(signal.to_dict(self.with_type()))
        return [{'id': id}]
