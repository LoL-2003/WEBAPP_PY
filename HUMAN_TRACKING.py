# import streamlit as st
# import paho.mqtt.client as mqtt
# import threading

# # HiveMQ Broker Details
# BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
# PORT = 8883
# USERNAME = "HUMAN_TRACKING"
# PASSWORD = "12345678aA"

# CONTROL_TOPIC = "esp32/control"
# STATUS_TOPIC = "esp32/status"

# # Streamlit UI settings
# st.set_page_config(page_title="ESP32 Control Panel", page_icon="🟢", layout="centered")

# st.title("🔌 ESP32 MQTT Control Panel")
# status_placeholder = st.empty()

# # Global variable for status
# device_status = "Unknown"

# # MQTT callback functions
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         client.subscribe(STATUS_TOPIC)
#     else:
#         st.error(f"Failed to connect: {rc}")

# def on_message(client, userdata, msg):
#     global device_status
#     message = msg.payload.decode()
#     if msg.topic == STATUS_TOPIC:
#         device_status = message
#         status_placeholder.markdown(f"### 🟢 Device Status: **{device_status}**")

# # MQTT client setup in a thread
# def start_mqtt():
#     client = mqtt.Client()
#     client.username_pw_set(USERNAME, PASSWORD)
#     client.tls_set()  # for secure connection
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(BROKER, PORT)
#     client.loop_forever()

# # Launch MQTT in background
# if "mqtt_started" not in st.session_state:
#     threading.Thread(target=start_mqtt, daemon=True).start()
#     st.session_state["mqtt_started"] = True

# # Command buttons
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("🔆 Turn ON"):
#         mqtt.Client().connect(BROKER, PORT)
#         pub = mqtt.Client()
#         pub.username_pw_set(USERNAME, PASSWORD)
#         pub.tls_set()
#         pub.connect(BROKER, PORT)
#         pub.publish(CONTROL_TOPIC, "ON")
#         st.success("Command 'ON' sent!")

# with col2:
#     if st.button("🌙 Turn OFF"):
#         pub = mqtt.Client()
#         pub.username_pw_set(USERNAME, PASSWORD)
#         pub.tls_set()
#         pub.connect(BROKER, PORT)
#         pub.publish(CONTROL_TOPIC, "OFF")
#         st.success("Command 'OFF' sent!")

# st.markdown("---")
# st.markdown("Developed by **Aditya Puri** 🚀")

import streamlit as st
import paho.mqtt.client as mqtt
import json
import threading
import time
import plotly.graph_objs as go
from collections import deque

# MQTT Credentials
MQTT_BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_TARGET = "esp32/target"
MQTT_TOPIC_STATUS = "esp32/status"
MQTT_TOPIC_CONTROL = "esp32/control"
MQTT_USERNAME = "HUMAN_TRACKING"
MQTT_PASSWORD = "12345678aA"

# Global state
status = "Offline"
sensor_data = {"x": 0, "y": 0, "speed": 0, "distance": 0}
data_buffer = deque(maxlen=100)

# MQTT Setup
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(MQTT_TOPIC_TARGET)
        client.subscribe(MQTT_TOPIC_STATUS)

def on_message(client, userdata, msg):
    global status, sensor_data, data_buffer
    if msg.topic == MQTT_TOPIC_STATUS:
        status = msg.payload.decode()
    elif msg.topic == MQTT_TOPIC_TARGET:
        try:
            payload = json.loads(msg.payload.decode())
            sensor_data.update(payload)
            data_buffer.append({
                "x": payload["x"],
                "y": payload["y"],
                "speed": payload["speed"],
                "distance": payload["distance"]
            })
        except Exception as e:
            print("JSON parse error:", e)

def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Start MQTT in background
threading.Thread(target=mqtt_thread, daemon=True).start()

# Streamlit UI
st.set_page_config(page_title="Human Tracking Dashboard", layout="wide", page_icon="📡")
st.title("📡 Real-Time Human Tracking Dashboard")

col1, col2 = st.columns([1, 3])

with col1:
    if status.lower() == "device online":
        st.markdown("**Status:** 🟢 Online")
    else:
        st.markdown("**Status:** 🔴 Offline")

    if st.button("Turn ON 🌞"):
        mqtt.Client().publish(MQTT_TOPIC_CONTROL, "ON")
    if st.button("Turn OFF 🌙"):
        mqtt.Client().publish(MQTT_TOPIC_CONTROL, "OFF")

st.success(f"Sent: {status}")

# Graph
st.markdown("## 📊 Real-Time Sensor Graph")
if len(data_buffer) > 0:
    xs = [d["x"] for d in data_buffer]
    ys = [d["y"] for d in data_buffer]
    speeds = [d["speed"] for d in data_buffer]
    distances = [d["distance"] for d in data_buffer]
    timestamps = list(range(len(data_buffer)))

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=timestamps, y=xs, mode='lines+markers', name='X'))
    fig.add_trace(go.Scatter(x=timestamps, y=ys, mode='lines+markers', name='Y'))
    fig.add_trace(go.Scatter(x=timestamps, y=speeds, mode='lines+markers', name='Speed'))
    fig.add_trace(go.Scatter(x=timestamps, y=distances, mode='lines+markers', name='Distance'))

    fig.update_layout(title="Sensor Data Over Time", xaxis_title="Time", yaxis_title="Values",
                      template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Waiting for data from ESP32...")

# Live values
st.markdown("## 🔍 Current Sensor Values")
st.metric(label="X", value=sensor_data["x"])
st.metric(label="Y", value=sensor_data["y"])
st.metric(label="Speed", value=sensor_data["speed"])
st.metric(label="Distance", value=sensor_data["distance"])
