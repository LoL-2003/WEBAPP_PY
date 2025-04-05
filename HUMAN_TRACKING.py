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
import queue
import json
import plotly.graph_objs as go
import time

# Page config
st.set_page_config(page_title="ESP32 Human Tracking", layout="centered", initial_sidebar_state="collapsed")

# Dark mode style
st.markdown("""
    <style>
        body { background-color: #121212; color: white; }
        .stMetric label, .stMetric div { color: #00ffb7; }
        h1 { color: #00ffb7 !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>ESP32 Human Tracking Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# Queue for MQTT messages
mqtt_queue = queue.Queue()

# Initialize session state
if 'plot_x' not in st.session_state:
    st.session_state.plot_x = []
    st.session_state.plot_y = []
    st.session_state.x = 0
    st.session_state.y = 0
    st.session_state.speed = 0
    st.session_state.distance = 0

# MQTT config
MQTT_BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "esp32/sensor"
MQTT_USERNAME = "HUMAN_TRACKING"
MQTT_PASSWORD = "12345678aA"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT connected.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT connection failed: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        mqtt_queue.put(data)
    except Exception as e:
        print("MQTT parsing error:", e)

# MQTT background thread
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_forever()

# Start thread once
if 'mqtt_started' not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_started = True

# Process MQTT messages (if any)
if not mqtt_queue.empty():
    data = mqtt_queue.get()
    st.session_state.x = data.get("x", 0)
    st.session_state.y = data.get("y", 0)
    st.session_state.speed = data.get("speed", 0)
    st.session_state.distance = data.get("distance", 0)
    st.session_state.plot_x.append(st.session_state.x)
    st.session_state.plot_y.append(st.session_state.y)

# Show metrics
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

col1.metric("X Coordinate", st.session_state.x)
col2.metric("Y Coordinate", st.session_state.y)
col3.metric("Speed", f"{st.session_state.speed:.2f}")
col4.metric("Distance", f"{st.session_state.distance:.2f}")

# Live plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=st.session_state.plot_x,
    y=st.session_state.plot_y,
    mode="lines+markers",
    line=dict(color="#00ffb7")
))
fig.update_layout(
    title="Live Target Path",
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#121212",
    font_color="#ffffff",
    xaxis_title="X",
    yaxis_title="Y",
)
st.plotly_chart(fig, use_container_width=True)

# Auto refresh every second
time.sleep(1)
st.experimental_rerun()
