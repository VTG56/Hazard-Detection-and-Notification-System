# app.py

from flask import Flask, render_template, jsonify
import serial
import threading
import time
import requests
from datetime import datetime
from collections import deque

app = Flask(__name__, template_folder="templates", static_folder="static")

# --- PUSHBULLET & NOTIFICATION LOG ---
PUSHBULLET_TOKEN = "o.bfpqJlkU6hbOl1TRwJx0D5wYAWmeXtGJ"  # ← Your Pushbullet Token
PUSHBULLET_API_URL = "https://api.pushbullet.com/v2/pushes"
HEADERS = {
    "Access-Token": PUSHBULLET_TOKEN,
    "Content-Type": "application/json"
}
# A thread-safe, fixed-size queue to store the last 10 notifications
notification_log = deque(maxlen=20) # Increased size for better logging

# --- TIMING & THRESHOLD CONSTANTS FROM BRIEF ---
# Notification timing and flags
last_notif_time = {"soil": 0, "smoke": 0, "ldr": 0, "flame": 0}

# Initial Notification Delay: Flame/Smoke: 0.5s, Moisture/LDR: 10s
NOTIF_DELAY_S = {"soil": 10, "smoke": 2, "ldr": 10, "flame": 2} 

# Hazard Escalation Delay: 30 seconds
CRITICAL_ESCALATION_DELAY_S = 10

sensor_data = {
    "soil": 0, "smoke": 0, "ldr": 0, "flame": 1,
    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# For Hazard Escalation Protocol
critical_condition_active_since = {
    "flame": 0,
    "smoke": 0,
    "soil_flood": 0,
    "ldr_bright": 0
}
escalated_notification_sent_flag = {
    "flame": False,
    "smoke": False,
    "soil_flood": False,
    "ldr_bright": False
}

def send_pushbullet_notification(title, body, severity="info"):
    """Sends a notification, logs it with a severity, and prints to console."""
    payload = {"type": "note", "title": title, "body": body}
    try:
        # Send to Pushbullet
        res = requests.post(PUSHBULLET_API_URL, json=payload, headers=HEADERS)
        log_timestamp = datetime.now().strftime('%H:%M:%S.%f') # Added microseconds for unique key
        
        # Log for frontend
        log_entry = {
            "timestamp": log_timestamp,
            "title": title,
            "body": body,
            "severity": severity # e.g., 'medium', 'critical', 'escalation'
        }
        notification_log.appendleft(log_entry)
        
        if res.status_code == 200:
            print(f"📨 [{severity.upper()}] Pushbullet notification sent: {title}")
        else:
            print(f"❌ Notification failed: {res.status_code} {res.text}")
            
    except Exception as e:
        print(f"⚠ Error sending Pushbullet notification: {e}")

# --- SENSOR DATA HANDLING ---
ser = None
SERIAL_PORT = 'COM5'
BAUD_RATE = 9600

def read_from_arduino():
    """Reads serial data from Arduino and triggers notification checks."""
    global sensor_data
    while True:
        if ser and ser.is_open:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line and len(line.split(',')) == 4:
                    parts = line.split(',')
                    sensor_data = {
                        "soil": int(parts[0]),
                        "smoke": int(parts[1]),
                        "ldr": int(parts[2]),
                        "flame": int(parts[3]),
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    check_and_send_notifications(sensor_data)
            except Exception as e:
                print(f"⚠ Error reading serial or processing data: {e}")
                time.sleep(2)
        else:
            time.sleep(5) # Wait before trying to reconnect

def check_and_send_notifications(data):
    """Checks sensor data and sends notifications based on the project brief."""
    global last_notif_time, critical_condition_active_since, escalated_notification_sent_flag
    current_time = time.time()

    # --- 1. Flame Sensor (Thermal & Combustion Sensor) ---
    is_flame_detected = data["flame"] == 0
    if is_flame_detected:
        if current_time - last_notif_time["flame"] > NOTIF_DELAY_S["flame"]:
            send_pushbullet_notification(
                "(NORMAL)🔥🔥 COMBUSTION EVENT DETECTED!",
                "Active flame detected in Sector Alpha! Immediately trigger fire suppression system. Evacuate sector now!",
                severity="critical"
            )
            last_notif_time["flame"] = current_time

        if critical_condition_active_since["flame"] == 0:
            critical_condition_active_since["flame"] = current_time
            escalated_notification_sent_flag["flame"] = False
        elif (current_time - critical_condition_active_since["flame"] > CRITICAL_ESCALATION_DELAY_S) and not escalated_notification_sent_flag["flame"]:
            send_pushbullet_notification(
                "(CRITICAL)🔥🔥 FIRE SPREADING!",
                "Combustion has not been suppressed for 30 seconds. Structural integrity is compromised. Jettison module protocol is now advised.",
                severity="escalation"
            )
            escalated_notification_sent_flag["flame"] = True
    else:
        critical_condition_active_since["flame"] = 0

    # --- 2. MQ-2 (Atmospheric Purity Sensor) ---
    is_gas_detected = data["smoke"] > 200
    if is_gas_detected:
        if current_time - last_notif_time["smoke"] > NOTIF_DELAY_S["smoke"]:
            send_pushbullet_notification(
                "(NORMAL)☣️ Cabin Air Contamination!",
                f"Unidentified volatile gases detected. Possible electrical short or propellant leak. Advise immediate crew mask deployment. (Smoke: {data['smoke']})",
                severity="critical"
            )
            last_notif_time["smoke"] = current_time

        if critical_condition_active_since["smoke"] == 0:
            critical_condition_active_since["smoke"] = current_time
            escalated_notification_sent_flag["smoke"] = False
        elif (current_time - critical_condition_active_since["smoke"] > CRITICAL_ESCALATION_DELAY_S) and not escalated_notification_sent_flag["smoke"]:
            send_pushbullet_notification(
                "(CRITICAL)☣️ ATMOSPHERE UNRECOVERABLE!",
                "Air quality remains critical for 30 seconds. Life support cannot scrub contaminants. Seal all hatches and prepare for EVA.",
                severity="escalation"
            )
            escalated_notification_sent_flag["smoke"] = True
    else:
        critical_condition_active_since["smoke"] = 0

    # --- 3. Moisture Sensor (Coolant Leak & Condensation) ---
    soil_value = data["soil"]
    is_flood_risk = soil_value < 400
    is_condensation_risk = 400 <= soil_value < 600

    if is_flood_risk:
        if current_time - last_notif_time["soil"] > NOTIF_DELAY_S["soil"]:
            send_pushbullet_notification(
                "(NORMAL)‼️ Alert: Fluid Leak Detected!",
                f"High moisture levels detected. Possible coolant line or water reclamation failure. Activate containment protocol. (Soil: {soil_value})",
                severity="critical"
            )
            last_notif_time["soil"] = current_time

        if critical_condition_active_since["soil_flood"] == 0:
            critical_condition_active_since["soil_flood"] = current_time
            escalated_notification_sent_flag["soil_flood"] = False
        elif (current_time - critical_condition_active_since["soil_flood"] > CRITICAL_ESCALATION_DELAY_S) and not escalated_notification_sent_flag["soil_flood"]:
            send_pushbullet_notification(
                "(CRITICAL)🚨 CATASTROPHIC FLOODING!",
                "Fluid leak has been continuous for 30 seconds. Containment failure imminent. Immediate EVACUATION of the sector is required!",
                severity="escalation"
            )
            escalated_notification_sent_flag["soil_flood"] = True
    else:
        critical_condition_active_since["soil_flood"] = 0
        if is_condensation_risk and (current_time - last_notif_time["soil"] > NOTIF_DELAY_S["soil"]):
            send_pushbullet_notification(
                "(NORMAL)💧 Atmospheric Condensation Alert",
                f"Humidity rising in Sector Gamma. Potential condensation on critical systems. Monitor telemetry. (Soil: {soil_value})",
                severity="medium"
            )
            last_notif_time["soil"] = current_time

    # --- 4. LDR (Ambient Light & Radiation Sensor) ---
    ldr_value = data["ldr"]
    is_extreme_luminosity = ldr_value <= 170
    is_unstable_light = 270 < ldr_value <= 700
    is_low_light = ldr_value > 700

    if is_extreme_luminosity:
        if current_time - last_notif_time["ldr"] > NOTIF_DELAY_S["ldr"]:
            send_pushbullet_notification(
                "(NORMAL)☀️ EXTREME LUMINOSITY EVENT!",
                f"Warning: Light intensity exceeds solar flare predictions. Possible external proximity event or hull breach. AVOID VISUAL EXPOSURE. (LDR: {ldr_value})",
                severity="critical"
            )
            last_notif_time["ldr"] = current_time

        if critical_condition_active_since["ldr_bright"] == 0:
            critical_condition_active_since["ldr_bright"] = current_time
            escalated_notification_sent_flag["ldr_bright"] = False
        elif (current_time - critical_condition_active_since["ldr_bright"] > CRITICAL_ESCALATION_DELAY_S) and not escalated_notification_sent_flag["ldr_bright"]:
            send_pushbullet_notification(
                "(CRITICALLLLLLL)☀️ HULL BREACH CONFIRMED!",
                "Extreme light exposure has been sustained for 30 seconds. Assume hull integrity is compromised. All crew to designated safe zones immediately.",
                severity="escalation"
            )
            escalated_notification_sent_flag["ldr_bright"] = True
    else:
        critical_condition_active_since["ldr_bright"] = 0
        #if is_unstable_light and (current_time - last_notif_time["ldr"] > NOTIF_DELAY_S["ldr"]):
        #    send_pushbullet_notification(
        #        "🌤 Unstable Light Fluctuation",
        #        f"Erratic light readings detected. Possible reflection from orbital debris or solar panel instability. Run external diagnostics. (LDR: {ldr_value})",
        #        severity="medium"
        #    )
         #   last_notif_time["ldr"] = current_time
        if is_low_light and (current_time - last_notif_time["ldr"] > NOTIF_DELAY_S["ldr"]):
            send_pushbullet_notification(
                "(NORMAL)🌑 Orbital Shadow or Power Anomaly",
                f"Module entering expected orbital shadow. If this is off-schedule, check primary power bus. Solar arrays show low input. (LDR: {ldr_value})",
                severity="info" # Low light is less of a warning
            )
            last_notif_time["ldr"] = current_time

# --- FLASK ROUTES ---
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/data')
def data():
    return jsonify(sensor_data)

@app.route('/notifications')
def notifications():
    return jsonify(list(notification_log))

# --- MAIN ---
if __name__ == '__main__':
    threading.Thread(target=read_from_arduino, daemon=True).start()
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print(f"✅ Connected to Arduino on {SERIAL_PORT}")
    except serial.SerialException as e:
        print(f"❌ Could not connect to {SERIAL_PORT}. Running in simulated mode. Error: {e}")
        ser = None
    app.run(debug=True, use_reloader=False)