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

# MQTT topics
TOPIC_SUB = "esp32/target"
TOPIC_PUB = "esp32/control"

# Global variables
client = None
received_messages = []
lock = threading.Lock()

# Callback functions
def on_connect(client, userdata, flags, rc):
    global received_messages
    if rc == 0:
        st.session_state.status = "✅ Connected to MQTT Broker"
        client.subscribe(TOPIC_SUB)
        st.write("Subscribed to topic:", TOPIC_SUB)
    else:
        st.session_state.status = f"❌ Failed to connect, return code {rc}"

def on_message(client, userdata, msg):
    global received_messages
    try:
        st.write(f"Message received on topic: {msg.topic}")  # Debug output
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
        st.session_state.messages = received_messages.copy()  # Force UI update
    except Exception as e:
        st.session_state.error = f"⚠️ Error decoding message: {str(e)}"

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
        st.write("Attempting to connect to MQTT broker...")
    except Exception as e:
        st.session_state.status = f"❌ Connection failed: {str(e)}"
    client.loop_start()

# Streamlit UI
def main():
    st.title("ESP32 MQTT Control Dashboard")

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

    # Status display
    st.subheader("Connection Status")
    st.write(st.session_state.status)

    # Control buttons
    st.subheader("LED Control")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Turn ON"):
            client.publish(TOPIC_PUB, "ON")
            st.success("✅ Command 'ON' sent to ESP32")
    with col2:
        if st.button("Turn OFF"):
            client.publish(TOPIC_PUB, "OFF")
            st.success("✅ Command 'OFF' sent to ESP32")

    # Received messages display
    st.subheader("Received Data")
    messages_placeholder = st.empty()
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            with st.expander(f"Message at {msg['timestamp']}"):
                st.write(f"X: {msg['x']}")
                st.write(f"Y: {msg['y']}")
                st.write(f"Speed: {msg['speed']}")
                st.write(f"Distance: {msg['distance']}")
    else:
        messages_placeholder.write("No messages received yet...")

    # Error display
    if st.session_state.error:
        st.error(st.session_state.error)

# Cleanup on app close
def cleanup():
    if client is not None:
        client.loop_stop()
        client.disconnect()

import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    main()
