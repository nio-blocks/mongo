from .mongodb_base_block import MongoDBBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.bool import BoolProperty
from nio.common.signal.base import Signal


@Discoverable(DiscoverableType.block)
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
        id = collection.save(signal.to_dict(self.with_type))
        return [Signal({'id': id})]
