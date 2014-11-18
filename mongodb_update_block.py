from .mongodb_base_block import MongoDBBase
from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.int import IntProperty
from nio.metadata.properties.bool import BoolProperty
from nio.common.signal.base import Signal
import ast


@Discoverable(DiscoverableType.block)
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
        spec (str): Expression property to query mongo. Should either be a
            string that is in the format of a dictionary or an expression that
            evaluates to a dictionary.
        document (int): Expresssion property used to make update. Should
            either be a string that is in the format of a dictionary or an
            expression that evaluates to a dictionary.
        upsert (str): Perform an upsert if True.
        multi (str): Perform update on only one matche if False.

    """
    spec = ExpressionProperty(title='Query Document',
                              default="{'id': {{$id}} }")
    document = ExpressionProperty(title='Update Document',
                                  default="{{ { '\$set': $.to_dict() } }}")
    upsert = BoolProperty(title='Upsert', default=False)
    multi = BoolProperty(title='Multi', default=False)

    def process_signals(self, signals):
        output = []
        for s in signals:
            try:
                collection = self._evaluate_collection(s)
                spec = self._evaluate_spec(s)
                spec = self._check_doc(spec, 'spec')
                document = self._evaluate_document(s)
                document = self._check_doc(document, 'document')
                output.extend(self._query_mongo(collection, spec, document))
            except:
                continue
        if output:
            self.notify_signals(output)

    def _evaluate_spec(self, signal):
        try:
            spec = self.spec(signal)
            return spec
        except Exception as e:
            self._logger.error("Spec failed to evaluate: {}".format(e))
            raise e

    def _evaluate_document(self, signal):
        try:
            document = self.document(signal)
            return document
        except Exception as e:
            self._logger.error("Document failed to evaluate: {}".format(e))
            raise e

    def _check_doc(self, doc, prop):
        if not doc:
            # if no doc is specified, then that is valid
            return {}
        if not isinstance(doc, dict):
            try:
                doc = ast.literal_eval(doc)
            except Exception as e:
                self._logger.error("{} needs to be a dict: "
                                   "{}".format(prop, doc))
                raise e
        if not isinstance(doc, dict):
            self._logger.error("{} needs to be a dict: "
                               "{}".format(prop, doc))
            raise e
        return doc

    def _query_mongo(self, collection, spec, document):
        output = []
        try:
            cursor = collection.update(spec=spec,
                                       document=document,
                                       upsert=self.upsert,
                                       multi=self.multi)
            output.append(Signal(cursor))
        except Exception as e:
            self._logger.error(
                "Error querying mongo: {}: {}".format(
                    type(e).__name__, str(e)))
            raise e
        return output
