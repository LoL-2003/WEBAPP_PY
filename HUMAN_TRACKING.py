import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import json
import time
from threading import Thread
from collections import deque
import plotly.graph_objects as go

# MQTT Broker Configuration
BROKER = "chameleon.lmq.cloudamqp.com"
PORT = 8883
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC = "esp32/target"

# Streamlit Page Setup
st.set_page_config(page_title="Target Tracker", layout="wide", page_icon="🎯")
st.markdown("## 🎯 Live Human Target Tracking Dashboard")

# Data queues
max_len = 100
x_vals, y_vals, speed_vals, distance_vals = deque(maxlen=max_len), deque(maxlen=max_len), deque(maxlen=max_len), deque(maxlen=max_len)

# MQTT Message Handler
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        x = data.get("x")
        y = data.get("y")
        speed = data.get("speed")
        distance = data.get("distance")

        x_vals.append(x)
        y_vals.append(y)
        speed_vals.append(speed)
        distance_vals.append(distance)
    except Exception as e:
        print("Error:", e)

# MQTT Connection Handler
def mqtt_thread():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    client.subscribe(TOPIC)
    client.loop_forever()

# Start MQTT in background
thread = Thread(target=mqtt_thread)
thread.daemon = True
thread.start()

# Streamlit Layout
col1, col2 = st.columns(2)
status_placeholder = st.empty()

# Live Update Loop
plot_placeholder1 = col1.empty()
plot_placeholder2 = col2.empty()

while True:
    if x_vals:
        # Plot X-Y position
        fig_xy = go.Figure()
        fig_xy.add_trace(go.Scatter(x=list(x_vals), y=list(y_vals),
                                    mode='markers+lines',
                                    marker=dict(size=10, color='lime'),
                                    line=dict(color='green')))
        fig_xy.update_layout(title="📍 Target X-Y Position",
                             xaxis_title="X",
                             yaxis_title="Y",
                             template="plotly_dark",
                             width=600, height=400)
        plot_placeholder1.plotly_chart(fig_xy, use_container_width=True)

        # Plot Speed & Distance
        fig_sd = go.Figure()
        fig_sd.add_trace(go.Scatter(y=list(speed_vals), name="Speed", line=dict(color='orange')))
        fig_sd.add_trace(go.Scatter(y=list(distance_vals), name="Distance", line=dict(color='cyan')))
        fig_sd.update_layout(title="🚀 Speed & Distance",
                             xaxis_title="Time (latest 100 points)",
                             template="plotly_dark",
                             width=600, height=400)
        plot_placeholder2.plotly_chart(fig_sd, use_container_width=True)
    time.sleep(0.5)
