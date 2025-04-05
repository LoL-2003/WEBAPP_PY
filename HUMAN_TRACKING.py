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
import plotly.graph_objs as go
from streamlit_autorefresh import st_autorefresh

# -------- Streamlit Page Config --------
st.set_page_config(page_title="Human Tracking Dashboard", layout="centered")
st.markdown("""
    <style>
    body {
        background-color: #121212;
        color: #E0E0E0;
    }
    .main {
        background-color: #1E1E1E;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------- MQTT Config --------
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
TOPIC = "esp32/tracking"
LED_TOPIC = "esp32/led"
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

# -------- Init Session State --------
if "mqtt_status" not in st.session_state:
    st.session_state["mqtt_status"] = "Connecting..."
if "latest_data" not in st.session_state:
    st.session_state["latest_data"] = {"x": 0, "y": 0, "speed": 0, "distance": 0}
if "led_state" not in st.session_state:
    st.session_state["led_state"] = False

# -------- MQTT Callbacks --------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state["mqtt_status"] = "Online"
        client.subscribe(TOPIC)
    else:
        st.session_state["mqtt_status"] = "Failed"

def on_disconnect(client, userdata, rc):
    st.session_state["mqtt_status"] = "Disconnected"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        parsed = json.loads(payload)
        if all(k in parsed for k in ("x", "y", "speed", "distance")):
            st.session_state["latest_data"] = parsed
    except Exception as e:
        print(f"[!] Error decoding MQTT: {e}")

# -------- MQTT Init (Once) --------
if "mqtt_client" not in st.session_state:
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    st.session_state["mqtt_client"] = client

# -------- Title & Status --------
st.title("📍 Human Tracking Dashboard")

mqtt_status = st.session_state.get("mqtt_status", "Connecting...")
status_color = "🟢" if mqtt_status == "Online" else "🔴"
st.markdown(f"### {status_color} MQTT Status: <code>{mqtt_status}</code>", unsafe_allow_html=True)

# -------- Live Tracking Metrics --------
data = st.session_state.get("latest_data", {"x": 0, "y": 0, "speed": 0, "distance": 0})
st.markdown("## 🛰️ Live Tracking Data")

col1, col2 = st.columns(2)
with col1:
    st.metric("🧭 X Coordinate", f"{data['x']}")
    st.metric("🏃 Speed", f"{data['speed']} m/s")
with col2:
    st.metric("🧭 Y Coordinate", f"{data['y']}")
    st.metric("📏 Distance", f"{data['distance']} m")

# -------- LED Toggle --------
st.markdown("---")
led_col = st.columns([1, 3, 1])[1]
with led_col:
    led_toggle = st.toggle("💡 LED Control", value=st.session_state["led_state"])

# Update LED state and publish if changed
if led_toggle != st.session_state["led_state"]:
    st.session_state["led_state"] = led_toggle
    led_msg = "ON" if led_toggle else "OFF"
    try:
        st.session_state["mqtt_client"].publish(LED_TOPIC, led_msg)
    except:
        st.warning("⚠️ MQTT not connected. LED command not sent.")

# -------- Real-Time Position Graph --------
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[0, data["x"]],
    y=[0, data["y"]],
    mode='lines+markers',
    marker=dict(color="lightgreen", size=10),
    line=dict(color="cyan", width=2)
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
st.plotly_chart(fig, use_container_width=True)

# -------- Auto Refresh --------
st_autorefresh(interval=1000, key="refresh")
