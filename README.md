# 🌡️ Real-Time Sensor Monitoring Dashboard

A web-based IoT dashboard that reads real-time data from multiple sensors using Arduino and displays it on a live web interface using Python Flask.

## 📦 Features

- 🌱 **Soil Moisture Monitoring** (Flood detection)
- 💨 **Smoke/Gas Detection**
- 💡 **LDR Light Intensity**
- 🔥 **Flame Detection**
- 🌡️ **Temperature Monitoring**
- 📊 Real-time updates every 2 seconds via Flask
- 🟢 Intuitive UI with colored alert indicators (green = normal, red = danger)
- 🧠 Easy to expand and integrate with ML models or alerts

---

## 🧰 Technologies Used

- ⚡ **Arduino Nano/Uno**
- 🐍 **Python 3**
- 🔌 **Flask** for the backend server
- 🧠 **HTML + JavaScript** for the frontend
- 🎨 **CSS (Gradient + Flexbox)** for styling
- 🧪 **Sensors Used**: Soil Moisture (analog), Smoke (MQ-2), LDR, Flame Sensor (digital), DHT11/DHT22

---

## 🔧 How It Works

### 🔌 Arduino Setup

- Collects data from sensors
- Sends a comma-separated string via serial (e.g. `600,350,720,1,28`)
- Format:  
  `soil,smoke,ldr,flame,temp`

### 🖥 Flask Server

- Listens on serial port (e.g. `COM7`)
- Parses incoming sensor data
- Hosts web dashboard on `http://127.0.0.1:5000`

---

## File Structure

```bash
project/
│
├── arduino_code.ino              # Arduino code for sensor readings
├── app.py                        # Python Flask backend
├── templates/
│   └── index.html                # Frontend UI
├── static/                       # (Optional) CSS or image assets
├── LICENSE                       # MIT License file
└── README.md
```

## Getting Started

1. Upload Arduino Code
   Upload your Arduino code using the Arduino IDE

2. Install Python Requirements

   ```bash
   pip install flask flask_socketio pyserial pandas joblib
   ```

3. Run Flask Server
   ```bash
   python app.py
   Then open your browser and go to: http://127.0.0.1:5000
   ```

## Troubleshooting

-Make sure only one program is accessing the COM port (close Arduino Serial Monitor).

-Check your COM port in app.py

-If data shows 0, ensure:
-Arduino is connected properly
-Baud rate is correct
-Sensors are wired and powered correctly

## Author

Tushar P
Email: tusharpradeep24@gmail.com
Github:@tung-programming

## License

[MIT LICENSE](LICENSE.md)
