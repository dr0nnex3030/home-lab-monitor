import os
import psutil
import requests
import time
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram(text):
    """Send a message to Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Token or Chat ID not found in .env!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        if response.status_code == 200:
            print(f"✅ Message sent: {text[:30]}...")
        else:
            print(f"❌ Telegram error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Request error: {e}")

def check_system():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('C:\\')

    # All messages in English
    message = f"🖥️ System Summary:\n"
    message += f"CPU: {cpu}%\n"
    message += f"RAM: {mem.percent}%\n"
    message += f"Disk C: {disk.percent}%"

    send_telegram(message)
    print("Summary sent.")

if __name__ == "__main__":
    print("🚀 Starting monitor...")
    check_system()
    # Uncomment for continuous monitoring every 60 seconds
    # while True:
    #     check_system()
    #     time.sleep(60)