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
import threading
import json
import plotly.graph_objs as go

# MQTT Settings
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

TOPIC_TRACKING = "esp32/tracking"
TOPIC_LED = "esp32/led"

# Streamlit UI settings
st.set_page_config(page_title="Human Tracking Dashboard", layout="centered")
st.title("📍 Human Tracking Dashboard")

# Realtime UI
status_placeholder = st.empty()
data_placeholder = st.empty()
plot_placeholder = st.empty()
led_placeholder = st.empty()

# Global state variables
device_status = "Connecting..."
latest_data = {"x": 0, "y": 0, "speed": 0, "distance": 0}
led_state = False

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    global device_status
    if rc == 0:
        device_status = "🟢 Online"
        client.subscribe(TOPIC_TRACKING)
    else:
        device_status = f"🔴 Failed (Code {rc})"

def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = msg.payload.decode()
        parsed = json.loads(payload)
        if all(k in parsed for k in ("x", "y", "speed", "distance")):
            latest_data = parsed
    except Exception as e:
        print(f"[!] MQTT decode error: {e}")

# Start MQTT in background thread
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

# Display status
status_placeholder.markdown(f"### {device_status}")

# Show tracking metrics
col1, col2 = st.columns(2)
col1.metric("🧭 X", latest_data["x"])
col1.metric("🏃 Speed", f"{latest_data['speed']} m/s")
col2.metric("🧭 Y", latest_data["y"])
col2.metric("📏 Distance", f"{latest_data['distance']} m")

# LED Toggle
led_state = led_placeholder.toggle("💡 LED", value=st.session_state.get("led", False))

# Publish LED control when toggled
if led_state != st.session_state.get("led", False):
    st.session_state["led"] = led_state
    pub = mqtt.Client()
    pub.username_pw_set(USERNAME, PASSWORD)
    pub.tls_set()
    pub.connect(BROKER, PORT)
    pub.publish(TOPIC_LED, "ON" if led_state else "OFF")

# Real-time Position Plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[0, latest_data["x"]],
    y=[0, latest_data["y"]],
    mode="lines+markers",
    marker=dict(color="orange", size=10),
    line=dict(color="cyan", width=2),
))
fig.update_layout(
    title="Real-Time Target Position",
    xaxis_title="X",
    yaxis_title="Y",
    template="plotly_dark",
    height=400
)
plot_placeholder.plotly_chart(fig, use_container_width=True)

# Refresh every 1 sec
st.experimental_rerun()
