import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import json
import math
import time
from threading import Thread
import plotly.graph_objects as go

# ---------------- MQTT CONFIG ---------------- #
BROKER = "chameleon.lmq.cloudamqp.com"
PORT = 8883
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC = "esp32/target"

# ---------------- STREAMLIT CONFIG ---------------- #
st.set_page_config(page_title="Live Target Tracker", layout="centered")
st.title("🎯 Live Target Tracking")

# ---------------- SHARED VARIABLES ---------------- #
latest_data = {"x": 0, "y": 0, "speed": 0.0, "distance": 0.0}
prev_data = {"x": 0, "y": 0, "timestamp": time.time()}

# ---------------- MQTT CALLBACKS ---------------- #
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global latest_data, prev_data
    try:
        payload = json.loads(msg.payload.decode())
        x = float(payload.get("x", 0))
        y = float(payload.get("y", 0))

        now = time.time()
        dx = x - prev_data["x"]
        dy = y - prev_data["y"]
        distance = math.sqrt(dx**2 + dy**2)
        dt = now - prev_data["timestamp"]
        speed = distance / dt if dt > 0 else 0.0

        latest_data.update({
            "x": x,
            "y": y,
            "distance": round(distance, 2),
            "speed": round(speed, 2)
        })

        prev_data.update({
            "x": x,
            "y": y,
            "timestamp": now
        })

    except Exception as e:
        st.error(f"Error in MQTT message: {e}")

# ---------------- START MQTT THREAD ---------------- #
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, 60)
    client.loop_forever()

Thread(target=mqtt_thread, daemon=True).start()

# ---------------- STREAMLIT DISPLAY LOOP ---------------- #
placeholder = st.empty()

while True:
    with placeholder.container():
        st.subheader("📍 Target Location")
        st.write(f"**X:** {latest_data['x']}  **Y:** {latest_data['y']}")
        st.write(f"**Distance moved:** {latest_data['distance']} units")
        st.write(f"**Speed:** {latest_data['speed']} units/sec")

        # Plot single point
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[latest_data["x"]],
            y=[latest_data["y"]],
            mode="markers",
            marker=dict(color="red", size=15),
            name="Live Target"
        ))
        fig.update_layout(
            xaxis_title="X Position",
            yaxis_title="Y Position",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[0, 100]),
            plot_bgcolor="black",
            paper_bgcolor="black",
            font_color="white",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    time.sleep(0.5)
