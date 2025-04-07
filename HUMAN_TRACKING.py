import streamlit as st
import paho.mqtt.client as mqtt
import json
import time
import math

st.set_page_config(page_title="Real-Time Human Tracking", layout="centered")
st.title("📡 Real-Time Human Tracking")
st.markdown("Live data from ESP32 via MQTT")

# # MQTT Credentials
# MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
# MQTT_PORT = 8883
# USERNAME = "xaygsnkk:xaygsnkk"
# PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC = "esp32/target"

#MQTT Broker settings (Cloud)
const char* mqtt_server = "fuji.lmq.cloudamqp.com";
const int mqtt_port = 8883;
const char* mqtt_username = "qthbfpde:qthbfpde"; // username
const char* mqtt_password = "Ct9dJehfPVqpIS6m0ZjDgVOgG-3EunYP";     // password

# Initialize values
x, y, speed, distance = 0.0, 0.0, 0.0, 0.0
prev_x, prev_y, prev_time = None, None, time.time()

# MQTT callback
def on_message(client, userdata, msg):
    global x, y, speed, distance, prev_x, prev_y, prev_time
    try:
        payload = json.loads(msg.payload.decode())
        new_x = float(payload.get("x", 0))
        new_y = float(payload.get("y", 0))
        curr_time = time.time()

        # Calculate distance and speed
        if prev_x is not None and prev_y is not None:
            dx = new_x - prev_x
            dy = new_y - prev_y
            dt = max(curr_time - prev_time, 0.01)
            distance = math.sqrt(dx**2 + dy**2)
            speed = distance / dt

        x, y = new_x, new_y
        prev_x, prev_y = new_x, new_y
        prev_time = curr_time

    except Exception as e:
        st.error(f"Error decoding message: {e}")

# MQTT setup
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# Display layout
col1, col2, col3, col4 = st.columns(4)
x_placeholder = col1.metric("X", "0.00")
y_placeholder = col2.metric("Y", "0.00")
speed_placeholder = col3.metric("Speed", "0.00 mm/s")
distance_placeholder = col4.metric("Distance", "0.00 mm")

# Live update loop
while True:
    x_placeholder.metric("X", f"{x:.2f}")
    y_placeholder.metric("Y", f"{y:.2f}")
    speed_placeholder.metric("Speed", f"{speed:.2f} units/s")
    distance_placeholder.metric("Distance", f"{distance:.2f} units")
    time.sleep(0.5)
