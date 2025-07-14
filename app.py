from flask import Flask, render_template, jsonify
import serial
import threading
import time
# Define this at top level
ser = None

app = Flask(__name__, template_folder="templates")

# --- CONFIGURATION ---
SERIAL_PORT = 'COM7'  # Change as needed (Linux: /dev/ttyUSB0)
BAUD_RATE = 9600
sensor_data = {
    "soil": 0,
    "smoke": 0,
    "ldr": 0,
    "temperature": 0.0,
    "flame": 1
}

# --- SERIAL READER THREAD ---
def read_from_arduino():
    global ser
    if ser is None:
        print("❌ Serial port not available.")
        return
    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            print(f"📥 Received: {line}")
            parts = line.split(',')
            if len(parts) == 5:
                sensor_data["soil"] = int(parts[0])
                sensor_data["smoke"] = int(parts[1])
                sensor_data["ldr"] = int(parts[2])
                sensor_data["temperature"] = float(parts[3])
                sensor_data["flame"] = int(parts[4])
        except Exception as e:
            print(f"⚠ Error reading serial: {e}")


# Start thread
threading.Thread(target=read_from_arduino, daemon=True).start()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    return jsonify(sensor_data)

# --- MAIN ---
if __name__ == '__main__':
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"❌ Serial error: {e}")
        ser = None

    # Start reading thread only once
    if ser:
        threading.Thread(target=read_from_arduino, daemon=True).start()

    app.run(debug=True,use_reloader=False)
