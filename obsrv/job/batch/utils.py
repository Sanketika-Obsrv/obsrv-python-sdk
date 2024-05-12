from pyspark.conf import SparkConf


def get_base_conf() -> SparkConf:
    conf = SparkConf()

    # conf.setMaster("local")  # Set master as local for testing
    # conf.set("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1")  # Include SQL Kafka to be able to write to kafka
    conf.set(
        "spark.hadoop.mapreduce.fileoutputcommitter.algorithm.version", "2"
    )  # Set output committer algorithm version
    conf.set("spark.speculation", "false")  # Disable speculation
    conf.set(
        "spark.hadoop.mapreduce.map.speculative", "false"
    )  # Disable map speculative execution
    conf.set(
        "spark.hadoop.mapreduce.reduce.speculative", "false"
    )  # Disable reduce speculative execution
    conf.set(
        "spark.sql.parquet.filterPushdown", "true"
    )  # Enable Parquet filter pushdown
    conf.set(
        "spark.sql.sources.partitionOverwriteMode", "dynamic"
    )  # Set partition overwrite mode
    conf.set(
        "spark.hadoop.mapreduce.input.fileinputformat.input.dir.recursive", "true"
    )  # Enable recursive directory listing
    conf.set(
        "spark.sql.execution.arrow.pyspark.enabled", "true"
    )  # Enable Apache Arrow optimization
    conf.set(
        "spark.executor.heartbeatInterval", "60s"
    )  # Set executor heartbeat interval
    conf.set("spark.network.timeout", "600s")  # Set network timeout
    conf.set("spark.sql.shuffle.partitions", "200")  # Set shuffle partitions
    conf.set("spark.default.parallelism", "200")  # Set default parallelism
    conf.set("spark.sql.session.timeZone", "UTC")  # Set timezone
    conf.set(
        "spark.sql.catalogImplementation", "hive"
    )  # Use Hive catalog implementation
    conf.set(
        "spark.sql.sources.partitionColumnTypeInference.enabled", "false"
    )  # Disable partition column type inference
    conf.set(
        "spark.hadoop.mapreduce.fileoutputcommitter.cleanup-failures.ignored", "true"
    )  # Ignore cleanup failures
    conf.set(
        "spark.hadoop.parquet.enable.summary-metadata", "false"
    )  # Disable summary metadata for Parquet
    conf.set("spark.sql.sources.ignoreCorruptFiles", "true")  # Ignore corrupt files
    conf.set("spark.sql.adaptive.enabled", "true")  # Enable adaptive query execution
    conf.set(
        "spark.sql.legacy.timeParserPolicy", "LEGACY"
    )  # Set time parser policy to LEGACY

    return conf
