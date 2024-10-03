from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, TimestampType

json_schema = StructType([
    StructField("event_id", StringType(), True),
    StructField("event_type", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("player_id", StringType(), True)
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

 
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "game_events") \
        .option("startingOffsets", "earliest") \
        .option("failOnDataLoss", "false") \
        .load()


    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), json_schema).alias("data")
    ).select("data.*")


    query = parsed_df.writeStream \
        .foreachBatch(print_parsed_data) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

    # Write batch to PostgreSQL
    batch_df.write \
        .jdbc(url=url, table="game_events", mode="append", properties=properties)

    print(f"Batch {batch_id} written to PostgreSQL.")

def print_kafka_message(df, epoch_id):
    df.show(truncate=False)
    print(df.select("event_id").take(1)[0]["event_type"].decode("utf-8"))

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

if __name__ == "__main__":
    main()
