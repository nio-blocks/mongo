from .mongodb_base_block import MongoDBBase
from nio.common.discovery import Discoverable, DiscoverableType
from nio.metadata.properties import ExpressionProperty
from nio.common.signal.base import Signal


@Discoverable(DiscoverableType.block)
class MongoDBCommand(MongoDBBase):

    """ A block for running mongo commands

    Properties:
        command (expr): Command to run against database. If command is a string
            then the command {*command*: 1} will be sent. Otherwise, command
            must be a dict and will be sent as is.

    """
    command = ExpressionProperty(title='Command',
                                 default='dbstats')

    def execute_query(self, collection, signal):
        command = self.evaluate_expression(self.command,
                                           signal,
                                           force_dict=False)
        self._logger.debug("Command: {}".format(command))
        sig = self._db.command(command)
        return [Signal(sig)]
