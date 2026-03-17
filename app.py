from flask import Flask, render_template, jsonify
import psutil
import logging
from datetime import datetime
import time

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)

def get_disk_path():
    """Get the primary disk path for different OS."""
    import platform
    if platform.system() == 'Windows':
        return 'C:/'
    return '/'

# Global variables for disk I/O tracking
_last_io_counters = None
_last_io_time = None

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
                               disk_percent=disk_percent)
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
        
        # Log high usage
        if cpu_percent > 90 or ram_percent > 90 or disk_space_percent > 90:
            logging.warning(f"High usage detected - CPU: {cpu_percent}%, RAM: {ram_percent}%, DISK: {disk_space_percent}%")
        
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
    app.run(debug=True)
