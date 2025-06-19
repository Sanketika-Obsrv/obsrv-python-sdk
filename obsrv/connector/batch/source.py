import argparse
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, final

from pyspark.conf import SparkConf
from pyspark.sql import DataFrame, SparkSession

from obsrv.common import ObsrvException
from obsrv.connector import ConnectorContext, ConnectorInstance, MetricsCollector
from obsrv.connector.batch.obsrv_dataset import ObsrvDataset
from obsrv.connector.registry import ConnectorRegistry
from obsrv.models import ErrorData, ExecutionMetric
from obsrv.utils import Config, EncryptionUtil, LoggerController

logger = LoggerController(__name__)


class ISourceConnector(ABC):

    @final
    def execute(self, ctx, sc, connector_config, operations_config, metrics_collector) -> Any:
        results = self.process(sc, ctx, connector_config, operations_config, metrics_collector)

        return results

    @abstractmethod
    def get_spark_conf(self, connector_config) -> SparkConf:
        pass

    @abstractmethod
    def process(self, sc, ctx, connector_config, operations_config, metrics_collector) -> Any:
        pass


class SourceConnector:

    @final
    def get_connector_instance(
        connector_instance_id: Any, postgres_config: Any
    ) -> ConnectorInstance:
        return ConnectorRegistry.get_connector_instance(
            connector_instance_id, postgres_config
        )

    @final
    def get_connector_config(connector_instance: ConnectorInstance) -> Dict[Any, Any]:
        return connector_instance.connector_config

    @final
    def get_operations_config(connector_instance: ConnectorInstance) -> Dict[Any, Any]:
        return connector_instance.operations_config

    @final
    def get_additional_config(spark_conf: SparkConf) -> SparkConf:
        addn_jars = ["org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1"]
        configured_jars = spark_conf.get("spark.jars.packages", "")
        if len(configured_jars):
            spark_conf.set(
                "spark.jars.packages", f"{configured_jars},{','.join(addn_jars)}"
            )
        else:
            spark_conf.set("spark.jars.packages", ",".join(addn_jars))
        return spark_conf

    @final
    def get_spark_session(
        ctx: ConnectorContext, connector_config: Dict[Any, Any], spark_conf: SparkConf
    ) -> SparkSession:
        spark_conf = SourceConnector.get_additional_config(spark_conf)
        try:
            sc = (
                SparkSession.builder.appName(ctx.connector_instance_id)
                .config(conf=spark_conf)
                .getOrCreate()
            )
            return sc
        except Exception as e:
            logger.exception(f"Error creating spark session: {str(e)}")

    @final
    def process_connector(
        connector: ISourceConnector,
        ctx: ConnectorContext,
        connector_config: Dict[Any, Any],
        config: Dict[Any, Any],
        sc: SparkSession,
        metrics_collector: MetricsCollector,
        operations_config: Dict[Any, Any],
    ) -> ExecutionMetric:
        valid_records, failed_records, framework_exec_time = 0, 0, 0
        results = connector.execute(
            ctx=ctx,
            sc=sc,
            connector_config=connector_config,
            operations_config=operations_config,
            metrics_collector=metrics_collector,
        )

        if isinstance(results, DataFrame):
            res = SourceConnector.process_result(results, ctx, config)
            valid_records += res[0]
            failed_records += res[1]
            framework_exec_time += res[2]
        else:
            for result in results:
                res = SourceConnector.process_result(result, ctx, config)
                valid_records += res[0]
                failed_records += res[1]
                framework_exec_time += res[2]

        return ExecutionMetric(
            totalRecords=valid_records + failed_records,
            failedRecords=failed_records,
            successRecords=valid_records,
            connectorExecTime=0,
            frameworkExecTime=framework_exec_time,
            totalExecTime=0,
        )

    def process_result(result, ctx, config):
        start_time = time.time()
        dataset = ObsrvDataset(result)
        dataset.to_event(ctx)
        dataset.append_obsrv_meta(ctx)

        dataset.filter_events(ctx, config)
        failed_events = dataset.invalid_events
        valid_events = dataset.valid_events
        dataset.save_to_kafka(config, ctx.entry_topic)
        failed_records_count = failed_events.count()
        valid_records_count = valid_events.count()
        end_time = time.time()

        return (valid_records_count, failed_records_count, end_time - start_time)

    @final
    def process(connector: ISourceConnector, **kwargs):
        args = SourceConnector.parse_args()

        config_file_path = (
            args.config_file_path
            if args.config_file_path
            else kwargs.get("config_file_path", None)
        )

        if config_file_path is None:
            raise Exception("Config file path not found")

        start_time = time.time()
        config = Config(config_file_path)
        connector_instance_id = (
            args.connector_instance_id
            if args.connector_instance_id
            else kwargs.get("connector_instance_id", None)
        )

        if connector_instance_id is None:
            raise Exception("Connector instance id not found")

        connector_instance = SourceConnector.get_connector_instance(
            connector_instance_id, config.find("postgres")
        )

        if connector_instance is None:
            raise Exception("Connector instance not found")

        ctx = connector_instance.connector_context
        # TODO: Move this to separate method
        ctx.building_block = config.find("building-block", None)
        ctx.env = config.find("env", None)
        connector_config = SourceConnector.get_connector_config(connector_instance)
        operations_config = SourceConnector.get_operations_config(connector_instance)
        # if 'is_encrypted' in connector_config and connector_config['is_encrypted']:
        encryption_util = EncryptionUtil(config.find("obsrv_encryption_key"))
        connector_config = json.loads(encryption_util.decrypt(connector_config))

        metrics_collector = MetricsCollector(ctx)
        sc = SourceConnector.get_spark_session(
            ctx, connector_config, connector.get_spark_conf(connector_config)
        )
        connector_processing_start = time.time()

        try:
            execution_metric = SourceConnector.process_connector(
                connector=connector,
                ctx=ctx,
                connector_config=connector_config,
                config=config,
                sc=sc,
                metrics_collector=metrics_collector,
                operations_config=operations_config,
            )
            end_time = time.time()

            metric_event = ExecutionMetric(
                totalRecords=execution_metric.totalRecords,
                failedRecords=execution_metric.failedRecords,
                successRecords=execution_metric.successRecords,
                connectorExecTime=end_time - connector_processing_start,
                frameworkExecTime=execution_metric.frameworkExecTime,
                totalExecTime=end_time - start_time,
            )
            metrics_collector.collect(metric=metric_event.to_json())

        except Exception as e:
            logger.exception(f"error processing connector: {str(e)}")
            ObsrvException(
                ErrorData(
                    "CONNECTOR_PROCESS_ERR", f"error processing connector: {str(e)}"
                )
            )

        finally:
            kafka_servers = config.find("kafka.broker-servers", "localhost:9092")
            compression_type = config.find("kafka.producer.compression", "snappy")

            sc.createDataFrame(
                metrics_collector.to_seq(), SourceConnector.get_metrics_schema()
            ).selectExpr("to_json(struct(*)) AS value").write.format("kafka").option(
                "kafka.bootstrap.servers", kafka_servers
            ).option(
                "kafka.compression.type", compression_type
            ).option(
                "topic", config.find("kafka.connector-metrics-topic")
            ).save()
            sc.stop()

    def get_metrics_schema():
        from pyspark.sql.types import (
            ArrayType,
            DoubleType,
            LongType,
            MapType,
            StringType,
            StructField,
            StructType,
        )

        schema = StructType(
            [
                StructField(
                    "actor", MapType(StringType(), StringType()), nullable=False
                ),
                StructField(
                    "context",
                    MapType(StringType(), MapType(StringType(), StringType())),
                    nullable=False,
                ),
                StructField(
                    "edata",
                    StructType(
                        [
                            StructField(
                                "labels",
                                ArrayType(MapType(StringType(), StringType())),
                                nullable=False,
                            ),
                            StructField(
                                "metric",
                                MapType(StringType(), DoubleType()),
                                nullable=False,
                            ),
                        ]
                    ),
                    nullable=False,
                ),
                StructField("eid", StringType(), nullable=False),
                StructField("ets", LongType(), nullable=False),
                StructField("mid", StringType(), nullable=False),
                StructField(
                    "object", MapType(StringType(), StringType()), nullable=False
                ),
            ]
        )

        return schema

    @final
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-f",
            "--config-file-path",
            help="Path to the config file containing the default connector configurations",
        )

        parser.add_argument(
            "-c",
            "--connector-instance-id",
            help="connector instance id",
        )

        parser.add_argument(
            "--connector.metadata.id",
            help="connector id",
        )

        args, unknown = parser.parse_known_args()
        return args
