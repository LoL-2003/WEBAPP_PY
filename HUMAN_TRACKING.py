import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import json
from datetime import datetime
import threading
import time

# CloudAMQP credentials
MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
MQTT_PORT = 8883
MQTT_USERNAME = "xaygsnkk:xaygsnkk"
MQTT_PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"

# MQTT topic
TOPIC_SUB = "esp32/target"

# Global variables
client = None
received_messages = []
lock = threading.Lock()
running = True

# Callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        st.session_state.status = "✅ Connected to MQTT Broker"
        client.subscribe(TOPIC_SUB)
        st.write(f"Subscribed to topic: {TOPIC_SUB}")
    else:
        st.session_state.status = f"❌ Failed to connect, return code {rc}"

def on_message(client, userdata, msg):
    try:
        st.write(f"Message received on topic: {msg.topic} - Payload: {msg.payload.decode()}")  # Debug output
        data = json.loads(msg.payload.decode())
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = {
            "timestamp": timestamp,
            "x": data.get("x", "N/A"),
            "y": data.get("y", "N/A"),
            "speed": data.get("speed", "N/A"),
            "distance": data.get("distance", "N/A")
        }
        with lock:
            received_messages.append(message)
            if len(received_messages) > 10:
                received_messages.pop(0)
        st.session_state.messages = received_messages.copy()  # Update session state
    except Exception as e:
        st.session_state.error = f"⚠️ Error decoding message: {str(e)}"
        st.write(f"Raw payload causing error: {msg.payload.decode()}")

# MQTT loop in a separate thread
def mqtt_loop():
    while running:
        client.loop(timeout=1.0)

# Initialize MQTT client
def init_mqtt():
    global client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        st.session_state.status = "⏳ Connecting..."
        threading.Thread(target=mqtt_loop, daemon=True).start()
    except Exception as e:
        st.session_state.status = f"❌ Connection failed: {str(e)}"

# Streamlit UI
def main():
    # Initialize session state
    if "status" not in st.session_state:
        st.session_state.status = "⏳ Connecting..."
    if "error" not in st.session_state:
        st.session_state.error = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize MQTT if not already done
    if client is None:
        init_mqtt()

    st.title("ESP32 MQTT Data Dashboard")

    # Status display
    st.subheader("Connection Status")
    st.write(st.session_state.status)

    # Received messages display
    st.subheader("Received Data")
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            with st.expander(f"Message at {msg['timestamp']}"):
                st.write(f"X: {msg['x']}")
                st.write(f"Y: {msg['y']}")
                st.write(f"Speed: {msg['speed']}")
                st.write(f"Distance: {msg['distance']}")
    else:
        st.write("No messages received yet...")

    # Error display
    if st.session_state.error:
        st.error(st.session_state.error)

# Cleanup on app close
def cleanup():
    global running, client
    running = False
    if client is not None:
        client.loop_stop()
        client.disconnect()

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    main()
