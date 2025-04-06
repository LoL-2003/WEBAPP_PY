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

# Streamlit Setup
st.set_page_config(page_title="Target Tracker", layout="centered", page_icon="🎯")
st.title("🎯 Live Target Location")

# Store latest positions (just last N points)
max_len = 50
x_vals, y_vals = deque(maxlen=max_len), deque(maxlen=max_len)

# MQTT Message Handler
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        x = data.get("x")
        y = data.get("y")

        x_vals.append(x)
        y_vals.append(y)
    except Exception as e:
        print("Error decoding MQTT:", e)

# Start MQTT in background
def mqtt_thread():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_message = on_message

    client.connect(BROKER, PORT, keepalive=60)
    client.subscribe(TOPIC)
    client.loop_forever()

thread = Thread(target=mqtt_thread)
thread.daemon = True
thread.start()

# Live location chart
placeholder = st.empty()

while True:
    with placeholder.container():
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(x_vals), y=list(y_vals),
                                 mode='markers+lines',
                                 marker=dict(size=10, color='red'),
                                 line=dict(color='lightgray')))
        fig.update_layout(
            xaxis_title="X Position",
            yaxis_title="Y Position",
            template="plotly_dark",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    time.sleep(0.5)
