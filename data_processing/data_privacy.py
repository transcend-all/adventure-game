# data_privacy.py
import hashlib
import json

class DataPrivacy:
    def __init__(self):
        """Initialize the data privacy module."""
        self.compliance_laws = ['GDPR', 'CCPA']  # List of supported privacy laws

    def anonymize_user_id(self, user_id):
        """Anonymize the user ID using a hashing algorithm (SHA-256)."""
        anonymized_id = hashlib.sha256(user_id.encode()).hexdigest()
        print(f"Anonymized User ID: {anonymized_id}")
        return anonymized_id

    def remove_sensitive_data(self, data):
        """Remove sensitive or personally identifiable information (PII) from the event data."""
        sensitive_keys = ['email', 'ip_address', 'phone_number']
        filtered_data = {key: value for key, value in data.items() if key not in sensitive_keys}
        print(f"Filtered Data: {json.dumps(filtered_data)}")
        return filtered_data

    def check_compliance(self, region):
        """Check if the data collection is compliant with regional privacy laws."""
        if region in ['EU', 'UK']:
            print("Data collection compliant with GDPR.")
            return 'GDPR'
        elif region == 'US':
            print("Data collection compliant with CCPA.")
            return 'CCPA'
        else:
            print("No specific privacy laws found for this region.")
            return 'None'

# Example usage
if __name__ == "__main__":
    # Initialize the privacy module
    privacy = DataPrivacy()

    # Simulate a player ID and region
    player_id = "player123"
    region = "EU"

    # Anonymize the player ID
    anonymized_id = privacy.anonymize_user_id(player_id)

    # Simulate event data with some PII
    event_data = {
        'user_id': player_id,
        'email': 'player123@example.com',
        'ip_address': '192.168.1.1',
        'phone_number': '123-456-7890',
        'event': 'purchase',
        'item': 'Health Potion'
    }

    # Remove sensitive data
    clean_data = privacy.remove_sensitive_data(event_data)

    # Check compliance with regional privacy laws
    privacy.check_compliance(region)
