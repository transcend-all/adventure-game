from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, ArrayType, IntegerType, DoubleType

json_schema = StructType([
    StructField("type", StringType(), True),
    StructField("data", StructType([
        StructField("player_position", ArrayType(IntegerType(), True))
    ]), True),
    StructField("timestamp", DoubleType(), True),
])

def main():
    # Initialize Spark Session with verbose logging
    spark = SparkSession.builder \
        .master("local[*]") \
        .appName("SimpleKafkaConsumer") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,org.apache.kafka:kafka-clients:3.4.0") \
        .getOrCreate()

    # Set log level to INFO for more detailed logging
    spark.sparkContext.setLogLevel("WARN")

    # def hex_to_string(hex_value):
    #     return bytes.fromhex(hex_value).decode('utf-8')

    # hex_to_string_udf = udf(hex_to_string, StringType())
 
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "game_events") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()

    decoded_df = kafka_df.select(
        col("value").cast(StringType())
    )

    parsed_df = decoded_df.select(
        from_json(col("value"), json_schema).alias("parsed_data")
    ).select("parsed_data.*")

    flattened_df = parsed_df.select(
        col("type").alias("event_type"),
        col("data.player_position").getItem(0).alias("player_x"),
        col("data.player_position").getItem(1).alias("player_y"),
        col("timestamp").cast(TimestampType())
    )

    query = flattened_df.writeStream \
        .foreachBatch(print_kafka_message) \
        .foreachBatch(write_to_postgres) \
        .outputMode("append") \
        .start()

    # query = parsed_df.writeStream \
    #     .foreachBatch(print_parsed_data) \
    #     .outputMode("append") \
    #     .start()

    query.awaitTermination()

    # Write batch to PostgreSQL
    batch_df.write \
        .jdbc(url=url, table="game_events", mode="append", properties=properties)

    print(f"Batch {batch_id} written to PostgreSQL.")

def print_kafka_message(df, epoch_id):
    df.show(truncate=False)
    print(df.select("event_type").take(1)[0]["event_type"])

def print_parsed_data(df, epoch_id):
    print(f"Parsed Batch ID: {epoch_id}")
    df.show(truncate=False)


def write_to_postgres(batch_df, batch_id):
    print(f"Writing batch {batch_id} to PostgreSQL...")
    # PostgreSQL connection properties
    url = "jdbc:postgresql://localhost:5432/adventure_game"
    properties = {
        "user": "adventure_game",
        "password": "adventure_game",
        "driver": "org.postgresql.Driver"
    }
    batch_df.write \
        .jdbc(url=url, table="game_events", mode="append", properties=properties)
    print(f"Batch {batch_id} written to PostgreSQL.")

if __name__ == "__main__":
    main()
