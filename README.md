# Home Lab Automation Suite

This repository contains Python scripts for automating system monitoring, local network scanning, and generating daily PDF reports for a home lab environment. All notifications and reports are sent directly to Telegram.

## 🔧 Features

- **System Monitor (`monitor.py`)**: Checks CPU, RAM, and disk usage. Sends real-time alerts and daily summaries to Telegram.
- **Network Scanner (`network_scanner.py`)**: Scans local network (192.168.0.0/24) for active devices (ping + port check) and sends the list to Telegram.
- **Daily Report Generator (`daily_report.py`)**: Collects system metrics (CPU/RAM/Disk/Uptime), top processes by CPU/Memory, network info (IP, MAC, Gateway), and generates a PDF report. The PDF is automatically sent to Telegram.

## 🛠️ Technologies Used

- **Python 3.10+**
- **psutil**: System monitoring and process management.
- **requests**: Telegram Bot API integration.
- **python-dotenv**: Secure storage of API credentials.
- **reportlab**: PDF generation.

## 🚀 Setup & Installation

1. Clone this repository.
2. Create a `.env` file in the root directory with your Telegram credentials: