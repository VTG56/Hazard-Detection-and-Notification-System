import requests from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access the key
API_KEY = os.getenv("API_KEY")

# Replace this with your actual Pushbullet Access Token
ACCESS_TOKEN = API_KEY;


# Message details
TITLE = "Hazard Alert"
BODY = "Sensor threshold crossed!"

def send_pushbullet_notification(title, body):
    data_send = {
        "type": "note",
        "title": title,
        "body": body
    }
    headers = {
        "Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post("https://api.pushbullet.com/v2/pushes", json=data_send, headers=headers)
    
    if response.status_code == 200:
        print("Notification sent successfully ✅")
    else:
        print(f"Failed to send notification ❌: {response.status_code}")
        print(response.text)

# Example usage
if __name__ == "__main__":
    send_pushbullet_notification(TITLE, BODY)
