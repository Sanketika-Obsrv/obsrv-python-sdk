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
import logging

# from obsrv.common import ObsrvException
from obsrv.job.batch import get_base_conf
from obsrv.connector.batch import ISourceConnector, SourceConnector
from obsrv.connector import ConnectorContext
from obsrv.connector import MetricsCollector
# from obsrv.models import ErrorData, StatusCode

from tests.create_tables import create_tables


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope='session', autouse=True)
def setUp(request):
    postgres = PostgresContainer("postgres:latest")
    kafka = KafkaContainer("confluentinc/cp-kafka:latest")

    postgres.start()
    kafka.start()

    with open(os.path.join(os.path.dirname(__file__), 'test_conf.yaml')) as config_file:
        config = yaml.safe_load(config_file)

        config['connector-instance-id'] = 'test.new-york-taxi-data.1'

        config['postgres']['host'] = postgres.get_container_host_ip()
        config['postgres']['port'] = postgres.get_exposed_port(5432)
        config['postgres']['user'] = postgres.username
        config['postgres']['password'] = postgres.password
        config['postgres']['dbname'] = postgres.dbname
        config['kafka']['bootstrap-servers'] = kafka.get_bootstrap_server()

    with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'w') as config_file:
        yaml.dump(config, config_file)

    create_tables(config)

    # clean up
    def remove_container():
        import time
        # logger.info("Waiting for 10 minutes before stopping the containers")
        # time.sleep(600)
        # input("Press Enter to continue...")
        postgres.stop()
        kafka.stop()
        os.remove(os.path.join(os.path.dirname(__file__), 'config.yaml'))

    request.addfinalizer(remove_container)

    # yield (postgres, kafka)

class TestSource(ISourceConnector):
    def process(self, sc: SparkSession, ctx: ConnectorContext, connector_config: Dict[Any, Any], metrics_collector: MetricsCollector) -> DataFrame:
        df = sc.read.format("json").load('tests/sample_data/nyt_data_100.json.gz')
        logging.info("Dataframe: %s", df.count())
        yield df

        df1 = sc.read.format("json").load('tests/sample_data/nyt_data_100.json')
        logging.info("Dataframe: %s", df1.count())
        yield df1

    def get_spark_conf(self, connector_config) -> SparkConf:
        conf = get_base_conf()
        logging.info("Spark Config: %s", conf.getAll())
        return conf

class TestBatchConnector(unittest.TestCase):
    def test_source_connector(self):
        connector = TestSource()
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

        config = yaml.safe_load(open(config_file_path))

        # print(config)
        # from obsrv.utils.config import Config
        # c = Config(config_file_path=config_file_path)
        # print(c.find("kafka.bootstrap-servers"))

        self.assertEqual(os.path.exists(config_file_path), True)

        test_raw_topic = 'test.ingest'
        test_metrics_topic = 'test.metrics'

        config = yaml.safe_load(open(config_file_path))

        kafka_consumer = KafkaConsumer(bootstrap_servers=config['kafka']['bootstrap-servers'], group_id='test-group', enable_auto_commit=True)

        trt_consumer = TopicPartition(test_raw_topic, 0)
        tmt_consumer = TopicPartition(test_metrics_topic, 0)

        kafka_consumer.assign([trt_consumer, tmt_consumer])
        # tmt_consumer = kafka_consumer.assign([tmt_consumer])

        kafka_consumer.seek_to_beginning()


        SourceConnector.process(connector=connector, config_file_path=config_file_path)

        metrics = []
        all_messages = kafka_consumer.poll(timeout_ms=10000)
        # kafka_consumer.commit('test-group')

        for topic_partition, messages in all_messages.items():
            for message in messages:
                logging.info("Infosys: %s", message.value)
                if topic_partition.topic == test_metrics_topic:
                    metrics.append(message.value)
                    # commit offset

        logging.info("metrics post process: %s", metrics)

        assert kafka_consumer.end_offsets([trt_consumer]) == {trt_consumer: 200}
        assert kafka_consumer.end_offsets([tmt_consumer]) == {tmt_consumer: 1}
