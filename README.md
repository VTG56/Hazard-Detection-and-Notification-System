# 🌡️ Real-Time Sensor Monitoring Dashboard

This project is a **real-time IoT dashboard** that reads data from multiple sensors connected to an Arduino and displays it on a live web interface. It uses a **Python Flask backend** to handle data processing and a clean frontend for visualization.

---

## 📦 Features
- 🌱 **Soil Moisture Monitoring**: Detects moisture levels to indicate potential floods or rain.  
- 💨 **Smoke/Gas Detection**: Monitors for gas or smoke to alert of fire hazards.  
- 💡 **LDR Light Intensity**: Measures ambient light.  
- 🔥 **Flame Detection**: Provides an immediate warning for flames.  
- 📊 **Real-time Updates**: Data is fetched from the Arduino and updated on the dashboard every 2 seconds.  
- 🟢 **Intuitive UI**: Modern design with color-coded alerts (green = normal, red = danger).  
- 📨 **Pushbullet Notifications**: Sends mobile alerts for critical events (e.g., high smoke levels or flame detection).  

---

## 🧰 Technologies Used
- ⚡ **Arduino Nano/Uno** – Reads sensor data  
- 🐍 **Python 3** – Backend programming language  
- 🔌 **Flask** – Lightweight web framework  
- 🧠 **HTML + JavaScript** – Interactive frontend  
- 🎨 **CSS (Gradient + Flexbox)** – Responsive and visually appealing UI  
- 📡 **Requests** – Python library for Pushbullet API calls  
- 📲 **Pushbullet API** – Sends real-time notifications to devices  

---

## 🔧 How It Works

### 🔌 Arduino Setup
- Reads values from sensors (soil moisture, smoke/gas, LDR, flame).  
- Formats readings as a CSV string:  
soil_value,smoke_value,ldr_value,flame_value
- Sends the string via **Serial** to the Flask server.  

### 🖥 Flask Server
- Listens on the **serial port** for incoming data.  
- Updates a global dictionary with the latest sensor readings.  
- Exposes `/data` API endpoint for frontend to fetch real-time values.  
- Checks thresholds → triggers **Pushbullet notifications** for critical alerts.  

## 📂 File Structure
project/
│
├── arduinofilemain.ino # Arduino code for sensor readings
├── app.py # Python Flask backend
├── templates/
│ └── index.html # Frontend UI
└── README.md # Project documentation

---

## 🚀 Getting Started

### 1. Upload Arduino Code
Upload `arduinofilemain.ino` to your Arduino using the Arduino IDE.  

### 2. Install Python Requirements:

pip install flask pyserial requests
### 3. Configure Pushbullet Notifications
Sign up at Pushbullet.

Get your Access Token from account settings.

In app.py, replace the placeholder for PUSHBULLET_TOKEN with your token.

### 4. Run the Flask Server
python app.py

### 5. Open Dashboard
Go to:
👉 http://127.0.0.1:5000
