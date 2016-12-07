from .mongodb_base import MongoDBBase
from nio.util.discovery import discoverable
from nio.properties import Property


@discoverable
class MongoDBCommand(MongoDBBase):

    """ A block for running mongo commands

    Properties:
        command (expr): Command to run against database. If command is a string
            then the command {*command*: 1} will be sent. Otherwise, command
            must be a dict and will be sent as is.

    """
    command = Property(title='Command',
                       default='dbstats')

    def execute_query(self, collection, signal):
        command = self.evaluate_expression(self.command,
                                           signal,
                                           force_dict=False)
        self.logger.debug("Command: {}".format(command))
        sig = self._db.command(command)
        return [sig]
