import os
import unittest
import yaml
import pytest
from typing import Any, Dict
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer
from kafka import KafkaConsumer, TopicPartition
from pyspark.sql import SparkSession, DataFrame
from pyspark.conf import SparkConf

# from obsrv.common import ObsrvException
from obsrv.job.batch import get_base_conf
from obsrv.connector.batch import ISourceConnector, SourceConnector
from obsrv.connector import ConnectorContext
from obsrv.connector import MetricsCollector
# from obsrv.models import ErrorData, StatusCode

from tests.create_tables import create_tables
from tests.batch_setup import setup_obsrv_database


class TestSource(ISourceConnector):
    def process(self, sc: SparkSession, ctx: ConnectorContext, connector_config: Dict[Any, Any], metrics_collector: MetricsCollector) -> DataFrame:
        df = sc.read.format("json").load('tests/sample_data/nyt_data_100.json.gz')
        yield df

        df1 = sc.read.format("json").load('tests/sample_data/nyt_data_100.json')
        yield df1

    def get_spark_conf(self, connector_config) -> SparkConf:
        conf = get_base_conf()
        return conf

@pytest.mark.usefixtures("setup_obsrv_database")
class TestBatchConnector(unittest.TestCase):
    def test_source_connector(self):

        connector = TestSource()
        config_file_path = os.path.join(os.path.dirname(__file__), 'config/config.yaml')

        config = yaml.safe_load(open(config_file_path))

        self.assertEqual(os.path.exists(config_file_path), True)

        test_raw_topic = 'test.ingest'
        test_metrics_topic = 'test.metrics'

        kafka_consumer = KafkaConsumer(bootstrap_servers=config['kafka']['bootstrap-servers'], group_id='test-group', enable_auto_commit=True)

        trt_consumer = TopicPartition(test_raw_topic, 0)
        tmt_consumer = TopicPartition(test_metrics_topic, 0)

        kafka_consumer.assign([trt_consumer, tmt_consumer])

        # kafka_consumer.seek_to_beginning()

        SourceConnector.process(connector=connector, config_file_path=config_file_path)

        # metrics = []
        # all_messages = kafka_consumer.poll(timeout_ms=10000)

        # for topic_partition, messages in all_messages.items():
        #     for message in messages:
        #         if topic_partition.topic == test_metrics_topic:
        #             metrics.append(message.value)

        assert kafka_consumer.end_offsets([trt_consumer]) == {trt_consumer: 200}
        assert kafka_consumer.end_offsets([tmt_consumer]) == {tmt_consumer: 1}
