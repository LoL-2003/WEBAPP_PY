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

st.title("📍 Human Tracking Dashboard")

# -------- MQTT Callbacks --------
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("esp32/target")
        client.subscribe("esp32/status")
        st.session_state["mqtt_status"] = "Device Online"
    else:
        st.session_state["mqtt_status"] = "Connection Failed"

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        if msg.topic == "esp32/target":
            parsed = json.loads(payload)
            if all(k in parsed for k in ("x", "y", "speed", "distance")):
                st.session_state["latest_data"] = parsed
        elif msg.topic == "esp32/status":
            st.session_state["mqtt_status"] = payload
    except Exception as e:
        print(f"[!] MQTT message error: {e}")

# -------- MQTT Init --------
if "mqtt_initialized" not in st.session_state:
    st.session_state["mqtt_initialized"] = True
    st.session_state["latest_data"] = {"x": 0, "y": 0, "speed": 0, "distance": 0}
    st.session_state["mqtt_status"] = "Connecting..."

    client = mqtt.Client()
    client.username_pw_set("HUMAN_TRACKING", "12345678aA")
    client.on_connect = on_connect
    client.on_message = on_message
    client.tls_set()
    client.connect("b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud", 8883, 60)
    client.loop_start()
    st.session_state["mqtt_client"] = client

# -------- Auto Refresh --------
st_autorefresh(interval=1000, key="mqtt-refresh")

# -------- Display Live Data --------
data = st.session_state["latest_data"]

st.markdown("### 📡 Live Tracking Data")
col1, col2 = st.columns(2)
with col1:
    st.metric("🧭 X Coordinate", f"{data['x']}")
    st.metric("🏃 Speed", f"{data['speed']} m/s")
with col2:
    st.metric("🧭 Y Coordinate", f"{data['y']}")
    st.metric("📏 Distance", f"{data['distance']} m")

# -------- Device Status --------
status_color = "🟢" if "Online" in st.session_state["mqtt_status"] else "🔴"
st.markdown(f"### {status_color} Status: **{st.session_state['mqtt_status']}**")

# -------- Control Buttons --------
st.markdown("### 🎮 Control Panel")
col_on, col_off = st.columns(2)
with col_on:
    if st.button("Turn ON"):
        client = st.session_state.get("mqtt_client")
        if client:
            client.publish("esp32/control", "ON")
with col_off:
    if st.button("Turn OFF"):
        client = st.session_state.get("mqtt_client")
        if client:
            client.publish("esp32/control", "OFF")

# -------- Real-time XY Plot --------
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[0, data["x"]],
    y=[0, data["y"]],
    mode='lines+markers',
    marker=dict(color="lightgreen", size=10),
    line=dict(color="cyan", width=2)
))
fig.update_layout(
    title="📍 Real-Time Target Position",
    xaxis_title="X Axis",
    yaxis_title="Y Axis",
    plot_bgcolor="#1E1E1E",
    paper_bgcolor="#1E1E1E",
    font=dict(color="#E0E0E0"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=False)
)
st.plotly_chart(fig, use_container_width=True)
