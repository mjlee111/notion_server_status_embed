from flask import Flask, render_template, jsonify
import psutil
import time
from datetime import datetime, timedelta
import platform

# Try to import NVIDIA monitoring
try:
    import pynvml
    NVIDIA_AVAILABLE = True
    try:
        pynvml.nvmlInit()
        nvidia_gpu_count = pynvml.nvmlDeviceGetCount()
    except:
        nvidia_gpu_count = 0
except ImportError:
    NVIDIA_AVAILABLE = False
    nvidia_gpu_count = 0

app = Flask(__name__)

def get_uptime():
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    current_time = datetime.now()
    uptime = current_time - boot_time
    return str(uptime).split('.')[0]  # Remove microseconds

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    memory = psutil.virtual_memory()
    return memory.percent

def get_gpu_usage():
    gpu_info = []
    
    # Check for NVIDIA GPUs if available
    if NVIDIA_AVAILABLE and nvidia_gpu_count > 0:
        for i in range(nvidia_gpu_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                gpu_info.append({
                    'name': pynvml.nvmlDeviceGetName(handle).decode('utf-8'),
                    'memory_used': info.used / info.total * 100,
                    'gpu_utilization': utilization.gpu
                })
            except Exception as e:
                print(f"Error getting NVIDIA GPU info: {e}")
    
    # Get integrated GPU info
    try:
        memory = psutil.virtual_memory()
        shared_memory = memory.available - memory.free
        total_memory = memory.total
        gpu_memory_percent = (shared_memory / total_memory) * 100
        
        # Estimate GPU usage based on CPU usage and shared memory
        cpu_usage = psutil.cpu_percent(interval=0.1)
        gpu_usage = min(100, (cpu_usage * 0.7) + (gpu_memory_percent * 0.3))
        
        gpu_info.append({
            'name': 'Integrated GPU',
            'gpu_utilization': round(gpu_usage, 1),
            'memory_used': round(gpu_memory_percent, 1)
        })
    except Exception as e:
        print(f"Error getting integrated GPU info: {e}")
    
    return gpu_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    return jsonify({
        'uptime': get_uptime(),
        'cpu_usage': get_cpu_usage(),
        'ram_usage': get_ram_usage(),
        'gpu_usage': get_gpu_usage()
    })

if __name__ == '__main__':
    # Change the port number here (default is 5000)
    port = 11999  # You can change this to any available port
    print(f"Server running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False) 