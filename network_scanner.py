import subprocess
import socket
import time
import requests
import datetime
import os
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

def scan_network(ip_range):
    """
    Scan all IPs from .1 to .254 in the given range.
    ip_range - string like "192.168.0" (first three octets).
    """
    print(f"Scanning network {ip_range}.0/24, this will take about a minute...")
    found_devices = []
    
    for i in range(1, 255):
        ip = f"{ip_range}.{i}"
        
        # 1. Try ping (Windows: ping -n 1, timeout 300ms)
        try:
            subprocess.check_output(
                ["ping", "-n", "1", "-w", "300", ip], 
                stderr=subprocess.DEVNULL, timeout=1
            )
            print(f"✅ Reply from {ip}")
            found_devices.append(ip)
            continue  # Ping successful, add and continue
        except:
            pass
        
        # 2. If ping didn't respond, try connecting to ports 80/443/22
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            result = sock.connect_ex((ip, 443))
            if result == 0:
                print(f"✅ Found on port 443: {ip}")
                found_devices.append(ip)
            else:
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.2)
                result = sock.connect_ex((ip, 80))
                if result == 0:
                    print(f"✅ Found on port 80: {ip}")
                    found_devices.append(ip)
            sock.close()
        except:
            pass

    if found_devices:
        # Send result to Telegram
        message = f"🖥️ **Scan completed**\n"
        message += f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        message += f"Devices found: {len(found_devices)}\n"
        message += "**IP list:**\n" + "\n".join(found_devices)
        send_telegram(message)
        print(f"🎉 Total devices found: {len(found_devices)}")
    else:
        send_telegram(f"😴 Scan of network {ip_range}.0/24 completed. No devices found.")
    
    return found_devices

if __name__ == "__main__":
    ip_input = input("Enter the first three octets of your network (e.g., 192.168.0): ")
    scan_network(ip_input)
