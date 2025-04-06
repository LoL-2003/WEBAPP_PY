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

# Real-time data variables
x, y, speed, distance = 0, 0, 0, 0
prev_x, prev_y = None, None
prev_time = time.time()

# History buffers
max_len = 50
x_history = deque(maxlen=max_len)
y_history = deque(maxlen=max_len)
speed_history = deque(maxlen=max_len)
distance_history = deque(maxlen=max_len)

# Callback on message receive
def on_message(client, userdata, msg):
    global x, y, speed, distance, prev_x, prev_y, prev_time

    try:
        payload = json.loads(msg.payload.decode())
        new_x = float(payload.get("x", 0))
        new_y = float(payload.get("y", 0))

        # Distance & speed calculation
        curr_time = time.time()
        if prev_x is not None and prev_y is not None:
            dx = new_x - prev_x
            dy = new_y - prev_y
            dt = max(curr_time - prev_time, 0.01)

            distance = math.sqrt(dx**2 + dy**2)
            speed = distance / dt
        else:
            distance, speed = 0, 0

        # Update variables
        x, y = new_x, new_y
        x_history.append(x)
        y_history.append(y)
        speed_history.append(speed)
        distance_history.append(distance)

        prev_x, prev_y = new_x, new_y
        prev_time = curr_time

    except Exception as e:
        st.error(f"Error parsing message: {e}")

# MQTT setup
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(USERNAME, PASSWORD)
client.on_message = on_message
client.tls_set()  # Use TLS for port 8883
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# UI placeholders
plot_placeholder = st.empty()
value_col1, value_col2, value_col3 = st.columns(3)

# Main loop
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
    fig.update_layout(
        xaxis_title="X Coordinate",
        yaxis_title="Y Coordinate",
        title="Live Target Location",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font_color="white",
        height=500
    )

    # Update Streamlit dashboard
    plot_placeholder.plotly_chart(fig, use_container_width=True)
    value_col1.metric("X", f"{x:.2f}")
    value_col2.metric("Y", f"{y:.2f}")
    value_col3.metric("Speed", f"{speed:.2f} units/s")

    time.sleep(0.5)
