# 🌡️ Real-Time Sensor Monitoring Dashboard
## This project is a real-time IoT dashboard that reads data from multiple sensors connected to an Arduino and displays it on a live web interface. It uses a Python Flask backend to handle the data processing and a clean frontend for visualization.
---
## 📦 Features
- 🌱 Soil Moisture Monitoring: Detects moisture levels to indicate potential floods or rain.

- 💨 Smoke/Gas Detection: Monitors for gas or smoke to alert of fire hazards.

- 💡 LDR Light Intensity: Measures ambient light.

- 🔥 Flame Detection: Provides an immediate warning for flames.

- 📊 Real-time Updates: Data is fetched from the Arduino and updated on the dashboard every 2 seconds.

- 🟢 Intuitive UI: Features a simple, modern design with color-coded alerts (green = normal, red = danger) for quick visual cues.

- 📨 Pushbullet Notifications: Automatically sends mobile alerts for critical events, such as high smoke levels or flame detection.
---
## 🧰 Technologies Used
- ⚡ Arduino Nano/Uno: The microcontroller for reading sensor data.

- 🐍 Python 3: The programming language used for the backend server.

- 🔌 Flask: A lightweight Python web framework for handling server-side logic and routing.

- 🧠 HTML + JavaScript: Used for building the interactive web frontend.

- 🎨 CSS (Gradient + Flexbox): Provides a responsive and visually appealing user interface.

- Requests: A Python library for making API calls to the Pushbullet service.

- Pushbullet API: Used to send push notifications to connected devices.
---
## 🔧 How It Works
- 🔌 Arduino Setup
The Arduino code is responsible for reading analog and digital values from the connected sensors. It formats this data into a comma-separated string (e.g., soil_value,smoke_value,ldr_value,flame_value) and sends it to the computer via the serial port.

- 🖥 Flask Server
The Python Flask server listens for the sensor data on a specified serial port. It processes the incoming string, updates a global dictionary with the latest readings, and makes this data available to the web frontend via a dedicated API endpoint (/data). The server also contains the core notification logic, checking sensor values against predefined thresholds and using the Pushbullet API to send alerts when necessary.
---
## File Structure
project/
│
├── arduinofilemain.ino         # Arduino code for sensor readings
├── app.py                      # Python Flask backend
├── templates/
│   └── index.html              # Frontend UI
└── README.md                   # Project documentation
---
## 🚀 Getting Started
- Upload the Arduino Code

- Upload the arduinofilemain.ino code to your Arduino board using the Arduino IDE.

- Install Python Requirements

- Open your terminal or command prompt and install the required libraries:
  pip install flask pyserial requests
- Configure Pushbullet Notifications

- Sign up for a free Pushbullet account and get your Access Token from your account settings.

- Open app.py and replace the placeholder value for PUSHBULLET_TOKEN with your actual token.

- Run the Flask Server

- Open your terminal, navigate to the project directory, and start the server:
-- python app.py
- Open your web browser and go to http://127.0.0.1:5000 to view the dashboard.

