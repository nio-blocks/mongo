from unittest import skipIf

from nio.testing.block_test_case import NIOBlockTestCase

pymongo_available = True
try:
    import pymongo
except:
    pymongo_available = False

MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DB = 'test'
MONGO_COLL = 'signals'


@skipIf(not pymongo_available, 'pymongo is not available!!')
class TestMongoBase(NIOBlockTestCase):

    """ A base test class for Mongo blocks """

    def __init__(self, method='runTests'):
        super().__init__(method)
        self.connection = None
        self.collection = None

    def setUp(self):
        super().setUp()
        # Clear out the collection before we start
        self.connection = pymongo.MongoClient(
            MONGO_HOST, MONGO_PORT)
        self.collection = self.connection[MONGO_DB][MONGO_COLL]

        self.collection.drop()

    def tearDown(self):
        # Clear out the collection again, to be safe
        self.collection.drop()
        self.connection.close()
        super().tearDown()

    def _get_conf(self, conf):
        """ Return the passed conf, merged with the server conf"""
        mongo_conf = {
            'connection': {
                'host': MONGO_HOST,
                'port': MONGO_PORT,
                'ssl': False
            },
            'database': MONGO_DB,
            'collection': MONGO_COLL,
            'log_level': 'DEBUG'
        }
        return dict(list(mongo_conf.items()) + list(conf.items()))
