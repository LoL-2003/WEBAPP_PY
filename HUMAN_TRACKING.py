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
import plotly.graph_objs as go

# MQTT Broker Configuration
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

# MQTT Topics
CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"
TRACKING_TOPIC = "esp32/data"

# Global State
device_status = "Unknown"
latest_data = {"x": 0, "y": 0, "speed": 0, "distance": 0}

# Streamlit Page Config
st.set_page_config(page_title="Human Tracking Dashboard", layout="centered")
st.title("📍 Human Tracking Dashboard")

# Placeholders for dynamic content
status_placeholder = st.empty()
data_placeholder = st.empty()
plot_placeholder = st.empty()

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(STATUS_TOPIC)
        client.subscribe(TRACKING_TOPIC)
    else:
        st.error(f"Failed to connect: {rc}")

def on_message(client, userdata, msg):
    global device_status, latest_data
    payload = msg.payload.decode()
    if msg.topic == STATUS_TOPIC:
        device_status = payload
        status_placeholder.markdown(f"### 🟢 Device Status: **{device_status}**")
    elif msg.topic == TRACKING_TOPIC:
        try:
            data = json.loads(payload)
            if all(k in data for k in ("x", "y", "speed", "distance")):
                latest_data.update(data)
        except Exception as e:
            print("Error parsing tracking data:", e)

# MQTT Thread Initialization
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True

# Control Buttons
st.markdown("### 💡 LED Control")
col1, col2 = st.columns(2)
with col1:
    if st.button("🔆 Turn ON"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "ON")
        st.success("Sent 'ON' command")

with col2:
    if st.button("🌙 Turn OFF"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "OFF")
        st.success("Sent 'OFF' command")

# Show Live Data
st.markdown("### 📡 Live Tracking Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("🧭 X Coordinate", f"{latest_data['x']}")
    st.metric("🏃 Speed", f"{latest_data['speed']} m/s")
with col2:
    st.metric("🧭 Y Coordinate", f"{latest_data['y']}")
    st.metric("📏 Distance", f"{latest_data['distance']} m")

# Real-time Plotting
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[0, latest_data["x"]],
    y=[0, latest_data["y"]],
    mode='lines+markers',
    marker=dict(color="lightgreen", size=10),
    line=dict(color="cyan", width=2),
    name='Position'
))
fig.update_layout(
    title="Real-Time Position",
    xaxis_title="X",
    yaxis_title="Y",
    plot_bgcolor="#1E1E1E",
    paper_bgcolor="#1E1E1E",
    font=dict(color="#E0E0E0"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)
plot_placeholder.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("Developed by **Aditya Puri** 🚀")
