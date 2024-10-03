# csv_logger.py
import csv
import os

class CSVLogger:
    def __init__(self, file_path):
        """Initialize the logger and ensure the CSV file is ready."""
        self.file_path = file_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # If the file does not exist, create it and add the header
        if not os.path.isfile(self.file_path):
            with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "event_type", "player_position"])

    def log_event(self, event_type, event_data):
        """Log the event to the CSV file."""
        with open(self.file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([event_data['timestamp'], event_type, event_data['player_position']])
