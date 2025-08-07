from flask import Flask, jsonify, request, send_from_directory
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import psutil
import datetime
import keyboard
import os
import threading
import webview
import time
import socket

app = Flask(__name__)
cpu_usage = 0.0

# Audio Interface initialisieren (Windows)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Initialen CPU-Auslastungswert setzen, damit cpu_percent() nicht 0 zurückgibt
psutil.cpu_percent(interval=None)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/script.js')
def script():
    return send_from_directory('.', 'script.js')

@app.route('/style.css')
def style():
    return send_from_directory('.', 'style.css')

@app.route('/api/system')
def api_system():
    global cpu_usage
    cpu =cpu_usage
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    now = datetime.datetime.now()

    # GPU-Daten (optional)
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        gpu_data = []
        for gpu in gpus:
            gpu_data.append({
                'name': gpu.name,
                'load': int(gpu.load * 100),
                'memoryUsed': gpu.memoryUsed,
                'memoryTotal': gpu.memoryTotal,
                'temperature': gpu.temperature
            })
    except ImportError:
        gpu_data = []
    local_ip, lan_ip = get_ip_addresses()
    return jsonify({
        'cpu': {
            'usage_percent': cpu,
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'frequency': {'current': psutil.cpu_freq().current if psutil.cpu_freq() else 0}
        },
        'ram': {
            'percent': ram.percent,
            'used_gb': round(ram.used / (1024**3), 2),
            'total_gb': round(ram.total / (1024**3), 2)
        },
        'disk': {
            'percent': disk.percent,
            'used_gb': round(disk.used / (1024**3), 2),
            'total_gb': round(disk.total / (1024**3), 2)
        },
        'network': {
            'sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'recv_mb': round(net_io.bytes_recv / (1024**2), 2)
        },
        'gpu': gpu_data,
        'system': {
            'os': os.name,
            'release': os.uname().release if hasattr(os, 'uname') else 'N/A',
            'processor': os.uname().machine if hasattr(os, 'uname') else 'N/A',
            'node': os.uname().nodename if hasattr(os, 'uname') else 'N/A'
        },
        'datetime': {
            'date': now.strftime("%Y-%m-%d"),
            'time': now.strftime("%H:%M:%S")
        },
        'ip': {
            'localhost': local_ip,
            'lan': lan_ip
        }
    })

def get_ip_addresses():
    # Always 127.0.0.1
    local_ip = "127.0.0.1"
    
    # Try to get LAN IP by opening a dummy socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # doesn't actually send data
        lan_ip = s.getsockname()[0]
        s.close()
    except Exception:
        lan_ip = "Unavailable"

    return local_ip, lan_ip

# Audio-Lautstärke auslesen & setzen
@app.route('/api/audio/volume', methods=['GET', 'POST'])
def audio_volume():
    if request.method == 'GET':
        current_volume = volume.GetMasterVolumeLevelScalar()
        is_muted = volume.GetMute()
        return jsonify({
            'volume': current_volume,
            'muted': bool(is_muted)
        })
    elif request.method == 'POST':
        data = request.json
        if 'volume' in data:
            v = float(data['volume'])
            if 0.0 <= v <= 1.0:
                volume.SetMasterVolumeLevelScalar(v, None)
        if 'muted' in data:
            muted = data['muted']
            volume.SetMute(1 if muted else 0, None)
        return jsonify({'status': 'ok'})

# Play/Pause Media-Taste senden
@app.route('/api/audio/playpause', methods=['POST'])
def audio_playpause():
    keyboard.send('play/pause media')
    return jsonify({'status': 'ok'})

def run_flask():
    # Flask im Hintergrund starten, ohne Debug und ohne Reload
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def cpu_monitor():
    global cpu_usage
    psutil.cpu_percent(interval=None)  # initialisieren
    while True:
        cpu_usage = psutil.cpu_percent(interval=1)  # blockiert 1 Sekunde

monitor_thread = threading.Thread(target=cpu_monitor, daemon=True)
monitor_thread.start()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Kurze Pause, damit Flask-Server Zeit zum Starten hat
    time.sleep(1)

    # Webview-Fenster öffnen
    webview.create_window('Control Panel', 'http://127.0.0.1:5000/', width=800, height=600, resizable=True)
    webview.start()
