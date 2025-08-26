from flask import Flask, render_template, jsonify
import serial
import threading
import time
import requests
from datetime import datetime
# --- PUSHBULLET CONFIGURATION ---
PUSHBULLET_TOKEN = "o.bfpqJlkU6hbOl1TRwJx0D5wYAWmeXtGJ"  # ← Replace this
PUSHBULLET_API_URL = "https://api.pushbullet.com/v2/pushes"
HEADERS = {
    "Access-Token": PUSHBULLET_TOKEN,
    "Content-Type": "application/json"
}

def send_pushbullet_notification(title, body):
    payload = {"type": "note", "title": title, "body": body}
    try:
        res = requests.post(PUSHBULLET_API_URL, json=payload, headers=HEADERS)
        if res.status_code == 200:
            print(f"📨 Pushbullet notification sent: {title}")
        else:
            print(f"❌ Notification failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"⚠ Error sending Pushbullet notification: {e}")

# Flags to avoid repeated alerts
notified = {
    "soil": False,
    "smoke": False,
    "ldr": False,
    "flame": False
}

# Last notification timestamps
lastnotif = {
    "soil": 0,
    "smoke": 0,
    "ldr": 0,
    "flame": 0
}

# Minimum seconds between notifications per sensor
notifdelay = {
    "soil": 10,    # notify once every 60 sec
    "smoke": 0.1,
    "ldr": 20,
    "flame": 0   # more aggressive (0 sec)
}


# --- FLASK & SERIAL SETUP ---
app = Flask(__name__, template_folder="templates")
SERIAL_PORT = 'COM5'     # Change if needed
BAUD_RATE     = 9600
ser           = None

sensor_data = {
    "soil": 0,
    "smoke": 0,
    "ldr": 0,
    #"temperature":    still tracked but no sensor attached
    "flame": 1
}

def read_from_arduino():
    global ser, sensor_data, notified

    if ser is None:
        print("❌ Serial port not available.")
        return

    while True:
        try:
            line = ser.readline().decode('utf-8').strip()
            if not line:
                continue

            print(f"📥 Received: {line}")
            parts = line.split(',')
            if len(parts) == 4:
                # Update readings
                sensor_data["soil"]        = int(parts[0])
                sensor_data["smoke"]       = int(parts[1])
                sensor_data["ldr"]         = int(parts[2])
                #sensor_data["temperature"] = float(parts[3])
                sensor_data["flame"]       = int(parts[3])
                print("Parsed sensor data:", sensor_data)
                print("\n")
                print("------------------------------------------------------------------------------------------")
                print("\n")

                # —— NOTIFICATION LOGIC ——
                ##################################################################
                # Soil moisture (flood risk)
                if sensor_data["soil"] <= 500 and not notified["soil"] and time.time() - lastnotif["soil"] > notifdelay["soil"]:
                    send_pushbullet_notification(
                        "🌊 Water Rising\nPossibility of flood",
                        f"Moisture level high: {sensor_data['soil']}"
                    )
                    lastnotif["soil"]=time.time()
                    notified["soil"] = True
                elif sensor_data["soil"] <= 600 and sensor_data["soil"] >= 530 and not notified["soil"] and time.time() - lastnotif["soil"] > notifdelay["soil"]:
                    send_pushbullet_notification(
                        "🌊 Moisture detected\nPossibility of rain",
                        f"Moisture level high: {sensor_data['soil']}"
                    )
                    lastnotif["soil"]=time.time()
                    notified["soil"] = True
                elif sensor_data["soil"] > 400:
                    notified["soil"] = False

                ###########################################################################
                # Smoke (MQ2)
                if sensor_data["smoke"] > 150 and not notified["smoke"]: #and time.time() - lastnotif["smoke"] > notifdelay["smoke"]:
                    send_pushbullet_notification(
                        "⚠️ Smoke Alert\nGas leak or fire!!!!!!",
                        f"High smoke level: {sensor_data['smoke']}"
                    )
                    lastnotif["smoke"]=time.time()
                    notified["smoke"] = True
                elif sensor_data["smoke"] <= 400:
                    notified["smoke"] = False

                ############################################################################
                # LDR (light/power)
                if sensor_data["ldr"] > 700 and not notified["ldr"] and time.time() - lastnotif["ldr"] > notifdelay["ldr"]:
                    send_pushbullet_notification(
                        "🌑 Low Light Detected\nPossibility of a power cut",
                        f"LDR reading: {sensor_data['ldr']}"
                    )
                    lastnotif["ldr"]=time.time()
                    notified["ldr"] = True
                elif sensor_data["ldr"] < 175 and not notified["ldr"] and time.time() - lastnotif["ldr"] > notifdelay["ldr"]:
                    send_pushbullet_notification(
                        "🌑 BRIGHT Light Detected" \
                        "\nPossibility of a Fire!!!",
                        f"LDR reading: {sensor_data['ldr']}"
                    )
                    lastnotif["ldr"]=time.time()
                    notified["ldr"] = True    
                elif sensor_data["ldr"] <= 700 and sensor_data["ldr"] >= 175:
                    notified["ldr"] = False
                #########################################################################
                # Flame sensor
                if sensor_data["flame"] == 0 and not notified["flame"]: #and time.time() - lastnotif["flame"] > notifdelay["flame"]:
                    send_pushbullet_notification(
                        "🔥 Flame Detected",
                        "Warning! Flame sensor triggered\nLOOK OUTT FOR FIREEEEEEEEEEEEEEEEEEE!!!!!!"
                    )
                    lastnotif["flame"]=time.time()
                    notified["flame"] = False
                elif sensor_data["flame"] != 0:
                    notified["flame"] = False

        except Exception as e:
            print(f"⚠ Error reading serial: {e}")

        time.sleep(0.1)  # small delay

# Start the serial reading thread
threading.Thread(target=read_from_arduino, daemon=True).start()

# ——— FLASK ROUTES ———
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    data_with_time = sensor_data.copy()
    data_with_time["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return jsonify(data_with_time)

# ——— MAIN ———
if __name__ == '__main__':
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"✅ Connected to {SERIAL_PORT}")
    except Exception as e:
        print(f"❌ Serial error: {e}")
        ser = None

    if ser:
        # (Already started above, but safe to ensure it’s running)
        threading.Thread(target=read_from_arduino, daemon=True).start()

    # Run Flask without reloader to avoid duplicate threads
    app.run(debug=True, use_reloader=False)
