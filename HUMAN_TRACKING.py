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

# Set dark theme
st.set_page_config(page_title="Human Tracking", layout="centered")

# Queue to receive MQTT data
mqtt_queue = queue.Queue()

# MQTT config
MQTT_BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC = "esp32/sensor"
MQTT_USERNAME = "HUMAN_TRACKING"
MQTT_PASSWORD = "12345678aA"

# Global variable to store last values
data_state = {"x": 0, "y": 0, "speed": 0, "distance": 0}

# MQTT callback
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT connected.")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ MQTT connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        mqtt_queue.put(data)
    except Exception as e:
        print("Error parsing MQTT message:", e)

# MQTT thread setup
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # Use SSL
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_forever()

# Start MQTT in background
threading.Thread(target=mqtt_thread, daemon=True).start()

# Streamlit UI
st.markdown("<h1 style='color:#00ffb7; text-align:center;'>ESP32 Human Tracking Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

x_val = st.empty()
y_val = st.empty()
speed_val = st.empty()
distance_val = st.empty()
plot_area = st.empty()

st.markdown("<style>body { background-color: #121212; color: white; }</style>", unsafe_allow_html=True)

# Real-time update loop
plot_x, plot_y = [], []

while True:
    if not mqtt_queue.empty():
        data = mqtt_queue.get()
        x = data.get("x", 0)
        y = data.get("y", 0)
        speed = data.get("speed", 0)
        distance = data.get("distance", 0)

        # Update UI
        x_val.metric("X Coordinate", x)
        y_val.metric("Y Coordinate", y)
        speed_val.metric("Speed", f"{speed:.2f}")
        distance_val.metric("Distance", f"{distance:.2f}")

        # Update data
        plot_x.append(x)
        plot_y.append(y)

        # Live plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_x, y=plot_y, mode="lines+markers", line=dict(color="#00ffb7")))
        fig.update_layout(
            plot_bgcolor="#1e1e1e",
            paper_bgcolor="#121212",
            font_color="#ffffff",
            title="Live X-Y Movement",
            xaxis_title="X Position",
            yaxis_title="Y Position",
        )
        plot_area.plotly_chart(fig, use_container_width=True)

    # Streamlit reruns every second
    st.experimental_rerun()
