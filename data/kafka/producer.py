from kafka import KafkaProducer
import json
import logging
import sys

class KafkaEventProducer:
    def __init__(self, bootstrap_servers=['localhost:9092'], topic='game_events'):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            self.topic = topic
            logging.info(f"Kafka producer initialized for topic '{self.topic}' on servers {bootstrap_servers}.")
        except Exception as e:
            logging.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None

    def send_event(self, event):
        if not self.producer:
            logging.error("Kafka producer is not initialized. Event not sent.")
            print("Kafka producer is not initialized. Event not sent.")  # Debugging line
            return
        try:
            future = self.producer.send(self.topic, event)
            result = future.get(timeout=10)  # Block until a single message is sent (or timeout)
            logging.debug(f"Event sent to Kafka: {event}")
            print(f"Event sent to Kafka: {event}")  # Debugging line
        except Exception as e:
            logging.error(f"Failed to send event to Kafka: {e}")
            print(f"Failed to send event to Kafka: {e}")  # Debugging line

    def close(self):
        if self.producer:
            try:
                self.producer.flush()
                self.producer.close()
                logging.info("Kafka producer closed successfully.")
            except Exception as e:
                logging.error(f"Failed to close Kafka producer: {e}")
