import smtplib
import re
import sys
import os
import logging
import requests
import json
from users import users_list
from skpy import Skype
from email.mime.text import MIMEText

credentials = json.loads(open("./credentials.json").read())

# Setup logging
LOG_FILE = "/var/log/ngrok_notifier.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Email configuration
EMAIL_FROM = "transcendentalguy@gmail.com"
EMAIL_TO = ["transcendentalguy@gmail.com"]
EMAIL_SUBJECT = "ngrok SSH Tunnel Info"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "transcendentalguy@gmail.com"
SMTP_PASSWORD = credentials["email_password"]

# Skype configuration
SKYPE_USERNAME = "transcend_all"
SKYPE_PASSWORD = credentials["skype_password"]
SKYPE_CONTACTS = users_list

# Path to ngrok output log file
NGROK_OUTPUT_LOG = "/tmp/ngrok_output.log"

def extract_ngrok_url():
    """Extract the ngrok public URL using the ngrok API."""
    logging.info("Extracting ngrok URL from ngrok API...")
    
    try:
        # Query the ngrok API
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        data = response.json()

        # Extract the public URL of the first tunnel
        for tunnel in data['tunnels']:
            if tunnel['proto'] == 'tcp':
                url = tunnel['public_url']
                logging.info(f"ngrok URL found: {url}")
                print(f"ngrok URL found: {url}")
                return url

    except Exception as e:
        logging.error(f"Failed to extract ngrok URL from API: {e}")
        print(f"Failed to extract ngrok URL from API: {e}")
        return None

    logging.error("ngrok URL not found in API.")
    print("ngrok URL not found in API.")
    return None

def send_email(url):
    """Send the ngrok URL via email."""
    logging.info("Sending email notification...")
    msg = MIMEText(f"ngrok SSH tunnel is active. Connect using the following URL: {url}")
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logging.info(f"Email sent to {EMAIL_TO}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def send_skype_message(url):
    """Send the ngrok URL via Skype."""
    try:
        # Log into Skype
        sk = Skype(SKYPE_USERNAME, SKYPE_PASSWORD)  # Skype object
        logging.info("Logged into Skype successfully")
        print("Logged into Skype successfully")

        # List all contacts to verify
        for contact in SKYPE_CONTACTS:
            if "live:" in contact:
                print(f"Sending message to contact: {contact}")
                sk.contacts[contact].chat.sendMsg(f"ngrok SSH tunnel is active: {url}")
            else:
                print(f"Sending message to group: {contact}")
                sk.chats[contact].sendMsg(f"ngrok SSH tunnel is active: {url}")
        
        logging.info(f"Skype message sent to contacts: {SKYPE_CONTACTS}")
        print(f"Skype message sent to contacts: {SKYPE_CONTACTS}")
    
    except Exception as e:
        logging.error(f"Failed to send Skype message: {e}")
        print(f"Failed to send Skype message: {e}")

def notify_failure():
    """Send failure notification via email."""
    logging.info("Sending failure notification...")
    msg = MIMEText("ngrok failed after 5 attempts to start.")
    msg["Subject"] = "ngrok Failure Notification"
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(EMAIL_TO)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        logging.info(f"Failure notification email sent to {EMAIL_TO}")
    except Exception as e:
        logging.error(f"Failed to send failure email: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--fail_notify':
        notify_failure()
        sys.exit(0)

    print("Extracting ngrok URL...")
    ngrok_url = extract_ngrok_url()
    # if ngrok_url:
    #     print("Sending email and Skype message...")
    #     send_email(ngrok_url)
    #     send_skype_message(ngrok_url)
    # else:
    #     logging.error("ngrok URL not found, no notifications sent.")
    #     print("ngrok URL not found, no notifications sent.")