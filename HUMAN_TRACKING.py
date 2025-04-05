import streamlit as st
import paho.mqtt.client as mqtt
import threading

# HiveMQ Broker Details
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"

# Streamlit UI settings
st.set_page_config(page_title="ESP32 Control Panel", page_icon="🟢", layout="centered")

st.title("🔌 ESP32 MQTT Control Panel")
status_placeholder = st.empty()

# Global variable for status
device_status = "Unknown"

# MQTT callback functions
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(STATUS_TOPIC)
    else:
        st.error(f"Failed to connect: {rc}")

def on_message(client, userdata, msg):
    global device_status
    message = msg.payload.decode()
    if msg.topic == STATUS_TOPIC:
        device_status = message
        status_placeholder.markdown(f"### 🟢 Device Status: **{device_status}**")

# MQTT client setup in a thread
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()  # for secure connection
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

# Launch MQTT in background
if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True

# Command buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔆 Turn ON"):
        mqtt.Client().connect(BROKER, PORT)
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "ON")
        st.success("Command 'ON' sent!")

with col2:
    if st.button("🌙 Turn OFF"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "OFF")
        st.success("Command 'OFF' sent!")

st.markdown("---")
st.markdown("Developed by **Aditya Puri** 🚀")

