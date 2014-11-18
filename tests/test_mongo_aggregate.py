from .test_mongo_base import TestMongoBase
from nio.common.signal.base import Signal
from ..mongodb_aggregation_block import MongoDBAggregation


class TestMongoAggregation(TestMongoBase):

    """ Tests the aggregation operations on a MongoDB """

    def setUp(self):
        super().setUp()

        self.collection.insert([
            {'type': 'A', 'val': 1},
            {'type': 'A', 'val': 2},
            {'type': 'A', 'val': 3},
            {'type': 'B', 'val': 10},
            {'type': 'B', 'val': -1},
            {'type': 'C', 'val': 5}
        ])

    def test_aggregation(self):

        blk = MongoDBAggregation()
        self.configure_block(blk, self._get_conf({
            "name": "AggregationBlock",
            "log_level": "DEBUG",
            "pipeline": [
                {"pipe": "{'$group': {'_id': '$type', " +
                         "'sum': {'$sum': '$val'}, " +
                         "'count': {'$sum': 1}}}"},
                {"pipe": "{'$sort': {'sum': -1}}"}
            ]
        }))

        blk.start()
        blk.process_signals([Signal()])
        blk.stop()

    def signals_notified(self, signals):
        # Should have 1 signal, with 3 vals in result
        self.assertEqual(len(signals), 1)
        self.assertEqual(len(signals[0].result), 3)

        # Results should be sorted in descending order of sum
        self.assertEqual(signals[0].result[0]['sum'], 9)
        self.assertEqual(signals[0].result[2]['sum'], 5)
