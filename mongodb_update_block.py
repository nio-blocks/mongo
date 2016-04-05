from .mongodb_base import MongoDBBase
from nio.util.discovery import discoverable
from nio.properties import Property
from nio.properties.bool import BoolProperty


@discoverable
class MongoDBUpdate(MongoDBBase):

    """ A block for updating a mongodb.

    The default spec and document properties are configured so that when if the
    mongo database already has the 'id' that the signal has, then mongo will be
    updated with all the properties of the incoming signal witout overriding
    any mongo fields that are not on the current signal. It assumes that 'id'
    is an integer. A string would need to look like:
        "{'id': '{{$id}}' }"
    Notice the quotes around {{$id}}.

    Properties:
        spec (str):  property to query mongo. Should either be a
            string that is in the format of a dictionary or an expression that
            evaluates to a dictionary.
        document (str): Expresssion property used to make update. Should
            either be a string that is in the format of a dictionary or an
            expression that evaluates to a dictionary.
        upsert (str): Perform an upsert if True.
        multi (str): Perform update on only one matche if False.

    """
    spec = Property(title='Query Document',
                              default="{'id': {{$id}} }")
    document = Property(title='Update Document',
                                  default="{{ { '\$set': $.to_dict() } }}")
    upsert = BoolProperty(title='Upsert', default=False)
    multi = BoolProperty(title='Multi', default=False)

    def query_args(self):
        existing_args = super().query_args()
        existing_args['upsert'] = self.upsert()
        existing_args['multi'] = self.multi()
        return existing_args

    def execute_query(self, collection, signal):
        spec = self.evaluate_expression(self.spec, signal)
        doc = self.evaluate_expression(self.document, signal)
        cursor = collection.update(spec=spec,
                                   document=doc,
                                   **(self.query_args()))

        return [cursor]
