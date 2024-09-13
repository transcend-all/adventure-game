# data_pipeline.py
import json
import time
from collections import deque

# Simulate an event streaming pipeline (like Apache Kafka)
class EventStream:
    def __init__(self):
        """Initialize the event stream for tracking user activity."""
        self.events = deque()  # A queue to store events

    def send_event(self, event_type, data):
        """Send an event to the pipeline."""
        event = {
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        self.events.append(event)
        print(f"Event sent: {json.dumps(event)}")

    def process_events(self):
        """Process events in the queue (could be stored in a database or used for real-time analytics)."""
        while self.events:
            event = self.events.popleft()
            # For now, we'll just print them, but these could be sent to a data lake or warehouse
            print(f"Processing event: {json.dumps(event)}")

# Simulate an analytics system
class Analytics:
    def __init__(self):
        """Initialize the analytics system."""
        self.user_activity = {}

    def track_event(self, user_id, event_type):
        """Track an event for a specific user."""
        if user_id not in self.user_activity:
            self.user_activity[user_id] = []
        self.user_activity[user_id].append({
            'event_type': event_type,
            'timestamp': time.time()
        })
        print(f"Tracked event for user {user_id}: {event_type}")

    def generate_report(self, user_id):
        """Generate a report on the player's activity."""
        if user_id in self.user_activity:
            print(f"User {user_id} activity report:")
            for event in self.user_activity[user_id]:
                print(f"- {event['event_type']} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event['timestamp']))}")
        else:
            print(f"No data available for user {user_id}")

# Example usage
if __name__ == "__main__":
    # Initialize the event stream and analytics systems
    event_stream = EventStream()
    analytics = Analytics()

    # Simulate player events
    player_id = "player123"
    event_stream.send_event("level_up", {"player_id": player_id, "new_level": 2})
    event_stream.send_event("coin_earned", {"player_id": player_id, "amount": 100})
    event_stream.send_event("item_purchased", {"player_id": player_id, "item": "Health Potion"})

    # Process the events (could be sent to a data lake or stored)
    event_stream.process_events()

    # Track and generate a report on the player's activity
    analytics.track_event(player_id, "level_up")
    analytics.track_event(player_id, "coin_earned")
    analytics.generate_report(player_id)
