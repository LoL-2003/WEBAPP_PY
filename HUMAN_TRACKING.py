import streamlit as st
import paho.mqtt.client as mqtt
import threading
import json

# HiveMQ Broker Details
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"
TARGET_TOPIC = "esp32/target"

# Shared state
status = "Connecting..."
data = {"x": None, "y": None, "speed": None, "distance": None}

# Streamlit UI settings
st.set_page_config(page_title="ESP32 Control Panel", page_icon="💡", layout="centered")
st.title("💡 ESP32 Control Panel")

col1, col2 = st.columns(2)
status_placeholder = col1.empty()

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(STATUS_TOPIC)
        client.subscribe(TARGET_TOPIC)
    else:
        print(f"Failed to connect: {rc}")

def on_message(client, userdata, msg):
    global status, data
    payload = msg.payload.decode()
    if msg.topic == STATUS_TOPIC:
        status = payload
        status_placeholder.markdown(f"**Status:** `{status}`")
    elif msg.topic == TARGET_TOPIC:
        print(f"[TARGET] Raw payload: {payload}")
        try:
            json_data = json.loads(payload)
            print(f"[TARGET] Decoded JSON: {json_data}")
            data.update(json_data)
        except Exception as e:
            print(f"[TARGET] Error decoding payload: {e}")

# MQTT Threading Setup
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

# Start MQTT once
if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True

# LED Control buttons
with col1:
    st.markdown("### 🔘 LED Control")
    if st.button("Turn ON"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "ON")
        st.success("Command 'ON' sent!")

    if st.button("Turn OFF"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "OFF")
        st.success("Command 'OFF' sent!")

# Target Data Display
def display_val(val):
    return val if val is not None else "..."

with col2:
    st.markdown("### 📍 Target Info")
    with st.empty():
        st.metric("X", display_val(data["x"]))
        st.metric("Y", display_val(data["y"]))
        st.metric("Speed", display_val(data["speed"]))
        st.metric("Distance", display_val(data["distance"]))

st.markdown("---")
st.markdown("Developed by **Aditya Puri** 🚀")
