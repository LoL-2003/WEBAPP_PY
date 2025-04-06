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

# Streamlit UI
st.set_page_config(page_title="Target Tracker", layout="centered")
st.title("🎯 Real-time Target Location")

# Store latest points
x_vals, y_vals = deque(maxlen=50), deque(maxlen=50)

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        x = data.get("x")
        y = data.get("y")

        if x is not None and y is not None:
            x_vals.append(x)
            y_vals.append(y)
    except Exception as e:
        print("MQTT Decode Error:", e)

# MQTT Background Thread
def mqtt_worker():
    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.subscribe(TOPIC)
    client.loop_forever()

Thread(target=mqtt_worker, daemon=True).start()

# Realtime Plot
plot_placeholder = st.empty()

while True:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(x_vals), y=list(y_vals),
                             mode='markers+lines',
                             marker=dict(size=10, color='red'),
                             line=dict(color='gray')))
    fig.update_layout(
        xaxis_title="X Position",
        yaxis_title="Y Position",
        height=500,
        template="plotly_dark"
    )
    plot_placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.5)
