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

# -------- Initialize Session State Keys --------
if "mqtt_initialized" not in st.session_state:
    st.session_state["mqtt_initialized"] = False
if "latest_data" not in st.session_state:
    st.session_state["latest_data"] = {"x": 0, "y": 0, "speed": 0, "distance": 0}
if "mqtt_status" not in st.session_state:
    st.session_state["mqtt_status"] = "Connecting..."
if "mqtt_client" not in st.session_state:
    st.session_state["mqtt_client"] = None

# -------- Custom Styling --------
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

st.title("📍 Human Tracking Dashboard")

# -------- MQTT Callback Functions --------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state["mqtt_status"] = "Online"
        client.subscribe("esp32/tracking")
    else:
        st.session_state["mqtt_status"] = f"Failed (code {rc})"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        parsed = json.loads(payload)
        if all(k in parsed for k in ("x", "y", "speed", "distance")):
            st.session_state["latest_data"] = parsed
    except Exception as e:
        print(f"[!] MQTT message error: {e}")

# -------- MQTT Initialization --------
if not st.session_state["mqtt_initialized"]:
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set("HUMAN_TRACKING", "12345678aA")  # Replace with your credentials
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.tls_set()  # SSL/TLS enabled
    mqtt_client.connect("b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud", 8883, 60)
    mqtt_client.loop_start()

    st.session_state["mqtt_initialized"] = True
    st.session_state["mqtt_client"] = mqtt_client

# -------- Auto Refresh --------
st_autorefresh(interval=1000, key="autorefresh")

# -------- Live Status & Data --------
status_color = "🟢" if "Online" in st.session_state["mqtt_status"] else "🔴"
st.markdown(f"### {status_color} MQTT Status: `{st.session_state['mqtt_status']}`")

data = st.session_state["latest_data"]

st.markdown("### 📡 Live Tracking Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("🧭 X Coordinate", f"{data['x']}")
    st.metric("🏃 Speed", f"{data['speed']} m/s")
with col2:
    st.metric("🧭 Y Coordinate", f"{data['y']}")
    st.metric("📏 Distance", f"{data['distance']} m")

# -------- Real-time Position Plot --------
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
