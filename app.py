from flask import Flask, render_template, jsonify
import psutil
import logging
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from plyer import notification

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from .env file
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 5000))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
DISK_PATH = os.getenv('DISK_PATH', 'C:/')
REFRESH_INTERVAL = int(os.getenv('REFRESH_INTERVAL', 2))
THRESHOLD_WARNING = int(os.getenv('THRESHOLD_WARNING', 80))
THRESHOLD_CRITICAL = int(os.getenv('THRESHOLD_CRITICAL', 90))
LOG_FILE = os.getenv('LOG_FILE', 'system_monitor.log')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_disk_path():
    """Get the disk path from configuration or default."""
    # If DISK_PATH is set in .env, use it. Otherwise, detect OS.
    if DISK_PATH:
        return DISK_PATH
    
    import platform
    if platform.system() == 'Windows':
        return 'C:/'
    return '/'

def send_notification(title, message):
    """Send a desktop notification if cooldown has passed."""
    global _last_notification_time
    current_time = time.time()
    
    if current_time - _last_notification_time > NOTIFICATION_COOLDOWN:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='Monitor de PC',
                timeout=10  # seconds
            )
            _last_notification_time = current_time
            logging.info(f"Notification sent: {title} - {message}")
        except Exception as e:
            logging.error(f"Failed to send notification: {e}")

# Global variables for disk I/O tracking
_last_io_counters = None
_last_io_time = None

# Global variable for notification cooldown
_last_notification_time = 0
NOTIFICATION_COOLDOWN = 60  # Seconds between notifications

@app.route('/')
def index():
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_percent = psutil.virtual_memory().percent
        disk_path = get_disk_path()
        disk_usage = psutil.disk_usage(disk_path)
        disk_percent = disk_usage.percent
        
        return render_template('index.html', 
                               cpu_percent=cpu_percent, 
                               ram_percent=ram_percent, 
                               disk_percent=disk_percent,
                               refresh_interval=REFRESH_INTERVAL * 1000) # Convert to milliseconds
    except Exception as e:
        logging.error(f"Error in index route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/data')
def data():
    global _last_io_counters, _last_io_time
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent
        
        # Disk Space Usage
        disk_path = get_disk_path()
        disk_usage = psutil.disk_usage(disk_path)
        disk_space_percent = disk_usage.percent
        
        # Disk Activity (Performance)
        current_io_counters = psutil.disk_io_counters()
        current_time = time.time()
        disk_activity_percent = 0
        
        if current_io_counters and _last_io_counters and _last_io_time:
            # Calculate time difference
            time_diff = current_time - _last_io_time
            
            # Calculate bytes read/written since last check
            bytes_read = current_io_counters.read_bytes - _last_io_counters.read_bytes
            bytes_written = current_io_counters.write_bytes - _last_io_counters.write_bytes
            total_bytes = bytes_read + bytes_written
            
            # Estimate activity percentage (simplified heuristic)
            # If 1MB transferred in 1 second, assume 100% activity
            # This is a rough approximation
            transfer_rate_mbps = (total_bytes / 1024 / 1024) / time_diff
            disk_activity_percent = min(100, transfer_rate_mbps * 10) # Scale factor to make it visible
        
        # Update last values
        _last_io_counters = current_io_counters
        _last_io_time = current_time
        
        # Log high usage based on thresholds
        if cpu_percent > THRESHOLD_CRITICAL or ram_percent > THRESHOLD_CRITICAL or disk_space_percent > THRESHOLD_CRITICAL:
            logging.warning(f"CRITICAL usage detected - CPU: {cpu_percent}%, RAM: {ram_percent}%, DISK: {disk_space_percent}%")
            # Send desktop notification for critical usage
            send_notification(
                "⚠️ Alerta Crítica de Recursos",
                f"CPU: {cpu_percent:.1f}% | RAM: {ram_percent:.1f}% | Disco: {disk_space_percent:.1f}%"
            )
        elif cpu_percent > THRESHOLD_WARNING or ram_percent > THRESHOLD_WARNING or disk_space_percent > THRESHOLD_WARNING:
            logging.info(f"High usage detected - CPU: {cpu_percent}%, RAM: {ram_percent}%, DISK: {disk_space_percent}%")
        
        return jsonify(
            cpu=cpu_percent, 
            ram=ram_percent, 
            disk_space=disk_space_percent, 
            disk_activity=disk_activity_percent
        )
    except Exception as e:
        logging.error(f"Error in data route: {e}")
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
