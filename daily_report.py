import os
import psutil
import socket
import datetime
import requests
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_document(filepath, caption=""):
    """Send a PDF document to Telegram."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("❌ Token or Chat ID not found in .env!")
        return
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    with open(filepath, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': CHAT_ID}
        if caption:
            data['caption'] = caption
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            print("✅ PDF report sent to Telegram!")
        else:
            print(f"❌ Telegram error: {response.status_code} - {response.text}")

def get_uptime():
    """Get system uptime in human-readable format."""
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.datetime.now() - boot_time
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    return f"{days} days, {hours} hours, {minutes} minutes"

def get_top_processes(limit=5):
    """Get top processes by CPU and memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    # Sort by CPU
    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]
    # Sort by memory
    top_mem = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:limit]
    return top_cpu, top_mem

def get_network_info():
    """Get IP, MAC, and gateway info."""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    # Get MAC address (first active interface)
    mac = "N/A"
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac = addr.address
                break
        if mac != "N/A":
            break
    # Get default gateway (on Windows)
    gateway = "N/A"
    try:
        import subprocess
        result = subprocess.check_output("ipconfig", text=True)
        # Parse gateway from ipconfig output (simple parse)
        for line in result.splitlines():
            if "Default Gateway" in line and ":" in line:
                gateway = line.split(":")[1].strip()
                break
    except:
        pass
    return hostname, local_ip, mac, gateway

def create_report():
    """Generate a detailed PDF report and send it via Telegram."""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('C:\\').percent
    uptime = get_uptime()
    top_cpu, top_mem = get_top_processes(5)
    hostname, ip, mac, gateway = get_network_info()
    
    filename = f"System_Report_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "System Report")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.drawString(100, 710, f"Hostname: {hostname}")
    c.drawString(100, 690, f"IP Address: {ip}")
    c.drawString(100, 670, f"MAC: {mac}")
    c.drawString(100, 650, f"Gateway: {gateway}")
    
    # System Metrics
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 610, "System Metrics")
    c.setFont("Helvetica", 12)
    c.drawString(100, 590, f"CPU: {cpu}%")
    c.drawString(100, 570, f"RAM: {mem}%")
    c.drawString(100, 550, f"Disk: {disk}%")
    c.drawString(100, 530, f"Uptime: {uptime}")
    
    # Top Processes
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 490, "Top Processes by CPU")
    c.setFont("Helvetica", 10)
    y = 470
    if top_cpu:
        for proc in top_cpu:
            c.drawString(120, y, f"{proc['name']} - CPU: {proc['cpu_percent']:.1f}%")
            y -= 15
    else:
        c.drawString(120, y, "No processes found")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 370, "Top Processes by Memory")
    c.setFont("Helvetica", 10)
    y = 350
    if top_mem:
        for proc in top_mem:
            c.drawString(120, y, f"{proc['name']} - Mem: {proc['memory_percent']:.1f}%")
            y -= 15
    else:
        c.drawString(120, y, "No processes found")
    
    # Network Devices (simple scan)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 250, "Active Network Devices")
    c.setFont("Helvetica", 10)
    # Quick scan of first 20 IPs
    devices = []
    for i in range(1, 20):
        ip = f"192.168.0.{i}"  # adjust to your network
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 80))
            if result == 0:
                devices.append(ip)
            sock.close()
        except:
            pass
    if devices:
        y = 230
        for dev in devices:
            c.drawString(120, y, dev)
            y -= 15
    else:
        c.drawString(120, 230, "No devices found")
    
    c.save()
    print(f"✅ PDF generated: {filename}")
    
    # Send to Telegram
    send_document(filename, caption="📊 Detailed Daily System Report")
    print("Report sent.")

if __name__ == "__main__":
    print("🚀 Generating detailed report...")
    create_report()