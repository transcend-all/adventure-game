from kafka import KafkaProducer
import json
import logging
import sys
import requests

# def get_ngrok_forwarding():
#     try:
#         response = requests.get('http://127.0.0.1:4040/api/tunnels')
#         data = response.json()
#         for tunnel in data['tunnels']:
#             if tunnel['proto'] == 'tcp':
#                 return tunnel['public_url'].replace('tcp://', '')
#     except Exception as e:
#         logging.error(f"Error fetching ngrok tunnel info: {e}")
#     return None

# # set bootstrap servers to ngrok forwarding, use in the future if the cluster is restarted
# bootstrap_servers = get_ngrok_forwarding()



class KafkaEventProducer:
    def __init__(self, bootstrap_servers=['4.tcp.us-cal-1.ngrok.io:17356'], topic='game_events'):
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
