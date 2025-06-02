import json
import time

from pyspark.sql import DataFrame
from pyspark.sql.functions import from_json, length, lit, struct, to_json
from pyspark.sql.types import StringType, StructField, StructType, LongType

from obsrv.utils import LoggerController

logger = LoggerController(__name__)


class ObsrvDataset:
    def __init__(self, ds: DataFrame):
        self.ds = ds
        self.invalid_events = None
        self.valid_events = None

    def filter_events(self, ctx, config):
        max_event_size = config.find("kafka.producer.max-request-size", 1000000)
        self.ds = self.ds.withColumn("_obsrv_tmp_size", length(to_json(struct("*"))))
        self.invalid_events = self.ds.filter(
            self.ds._obsrv_tmp_size > max_event_size
        ).drop("_obsrv_tmp_size")
        self.valid_events = self.ds.filter(
            self.ds._obsrv_tmp_size <= max_event_size
        ).drop("_obsrv_tmp_size")

    def to_event(self, ctx):
        columns = self.ds.columns
        ds = self.ds.withColumn("event", struct(*columns))
        ds = ds.drop(*columns)
        ds = ds.withColumn("dataset", lit(ctx.dataset_id))
        self.ds = ds

    def append_obsrv_meta(self, ctx):
        addn_meta = False

        source_meta = [
            StructField("connector", StringType(), True),
            StructField("connectorInstance", StringType(), True),
        ]
        # if "_addn_source_meta" in self.ds.columns:
        #     addn_meta = True
        #     source_meta.append(StructField("_addn_source_meta", StringType(), True))
        #     addn_meta_data = (
        #         self.ds.select("_addn_source_meta").collect()[0][0].replace('"', "'")
        #     )
        #     self.ds = self.ds.drop("_addn_source_meta")

        obsrv_meta_schema = StructType(
            [
                StructField("syncts", LongType(), True),
                StructField("flags", StructType(), True),
                StructField("timespans", StructType(), True),
                StructField("error", StructType(), True),
                StructField("source", StructType(source_meta), True),
            ]
        )

        syncts = int(time.time() * 1000)
        obsrv_meta = {
            "syncts": syncts,
            "flags": {},
            "timespans": {},
            "error": {},
            "source": {
                "connector": ctx.connector_id,
                "connectorInstance": ctx.connector_instance_id,
            },
        }

        if addn_meta:
            obsrv_meta["source"]["_addn_source_meta"] = addn_meta_data

        obsrv_meta_struct = from_json(lit(json.dumps(obsrv_meta)), obsrv_meta_schema)
        self.ds = self.ds.withColumn("obsrv_meta", obsrv_meta_struct)

    def save_to_kafka(self, config, topic):
        kafka_servers = config.find("kafka.broker-servers", "localhost:9092")
        compression_type = config.find("kafka.producer.compression", "snappy")

        self.valid_events.selectExpr("to_json(struct(*)) AS value").write.format(
            "kafka"
        ).option("kafka.bootstrap.servers", kafka_servers).option(
            "kafka.compression.type", compression_type
        ).option(
            "topic", topic
        ).save()

        # TODO: Handle invalid events - send to dead letter queue
