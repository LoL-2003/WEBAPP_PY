import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import plotly.graph_objects as go
import math
from collections import deque
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

st.set_page_config(page_title="Live Human Tracking", layout="wide")
st.title("📡 Real-Time Human Tracking")
st.markdown("Live data from ESP32 via MQTT")

# MQTT Setup
MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
MQTT_PORT = 8883
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC = "esp32/target"

# Variables to store real-time data
x, y, speed, distance = 0, 0, 0, 0
prev_x, prev_y = None, None
prev_time = time.time()

# Store last N positions
max_len = 50
x_history = deque(maxlen=max_len)
y_history = deque(maxlen=max_len)
speed_history = deque(maxlen=max_len)
distance_history = deque(maxlen=max_len)

# Callback when a message is received
def on_message(client, userdata, msg):
    global x, y, speed, distance, prev_x, prev_y, prev_time

    try:
        payload = json.loads(msg.payload.decode())
        new_x = float(payload.get("x", 0))
        new_y = float(payload.get("y", 0))

        # Calculate distance and speed
        curr_time = time.time()
        if prev_x is not None and prev_y is not None:
            dx = new_x - prev_x
            dy = new_y - prev_y
            dt = curr_time - prev_time if curr_time - prev_time > 0 else 0.01

            distance = math.sqrt(dx**2 + dy**2)
            speed = distance / dt
        else:
            distance, speed = 0, 0

        # Update history
        x, y = new_x, new_y
        x_history.append(x)
        y_history.append(y)
        speed_history.append(speed)
        distance_history.append(distance)

        prev_x, prev_y = new_x, new_y
        prev_time = curr_time

    except Exception as e:
        st.error(f"Error parsing message: {e}")

# MQTT client setup
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)
client.loop_start()

# Streamlit chart loop
plot_placeholder = st.empty()
value_col1, value_col2, value_col3 = st.columns(3)

while True:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(x_history),
        y=list(y_history),
        mode='lines+markers+text',
        marker=dict(color='red', size=8),
        line=dict(color='gray', width=2),
        text=[f"({round(px,1)}, {round(py,1)})" for px, py in zip(x_history, y_history)],
        textposition="top center",
        name="Path"
    ))

