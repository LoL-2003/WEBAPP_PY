# import streamlit as st
# import paho.mqtt.client as mqtt
# import threading

# # HiveMQ Broker Details
# BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
# PORT = 8883
# USERNAME = "HUMAN_TRACKING"
# PASSWORD = "12345678aA"

# CONTROL_TOPIC = "esp32/control"
# STATUS_TOPIC = "esp32/status"

# # Streamlit UI settings
# st.set_page_config(page_title="ESP32 Control Panel", page_icon="🟢", layout="centered")

# st.title("🔌 ESP32 MQTT Control Panel")
# status_placeholder = st.empty()

# # Global variable for status
# device_status = "Unknown"

# # MQTT callback functions
# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         client.subscribe(STATUS_TOPIC)
#     else:
#         st.error(f"Failed to connect: {rc}")

# def on_message(client, userdata, msg):
#     global device_status
#     message = msg.payload.decode()
#     if msg.topic == STATUS_TOPIC:
#         device_status = message
#         status_placeholder.markdown(f"### 🟢 Device Status: **{device_status}**")

# # MQTT client setup in a thread
# def start_mqtt():
#     client = mqtt.Client()
#     client.username_pw_set(USERNAME, PASSWORD)
#     client.tls_set()  # for secure connection
#     client.on_connect = on_connect
#     client.on_message = on_message
#     client.connect(BROKER, PORT)
#     client.loop_forever()

# # Launch MQTT in background
# if "mqtt_started" not in st.session_state:
#     threading.Thread(target=start_mqtt, daemon=True).start()
#     st.session_state["mqtt_started"] = True

# # Command buttons
# col1, col2 = st.columns(2)
# with col1:
#     if st.button("🔆 Turn ON"):
#         mqtt.Client().connect(BROKER, PORT)
#         pub = mqtt.Client()
#         pub.username_pw_set(USERNAME, PASSWORD)
#         pub.tls_set()
#         pub.connect(BROKER, PORT)
#         pub.publish(CONTROL_TOPIC, "ON")
#         st.success("Command 'ON' sent!")

# with col2:
#     if st.button("🌙 Turn OFF"):
#         pub = mqtt.Client()
#         pub.username_pw_set(USERNAME, PASSWORD)
#         pub.tls_set()
#         pub.connect(BROKER, PORT)
#         pub.publish(CONTROL_TOPIC, "OFF")
#         st.success("Command 'OFF' sent!")

# st.markdown("---")
# st.markdown("Developed by **Aditya Puri** 🚀")

import streamlit as st
import paho.mqtt.client as mqtt
import json
import threading

# MQTT Configuration
MQTT_BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
MQTT_PORT = 8884
MQTT_USERNAME = "HUMAN_TRACKING"
MQTT_PASSWORD = "12345678aA"
MQTT_TOPIC_TARGET = "esp32/target"
MQTT_TOPIC_STATUS = "esp32/status"
MQTT_TOPIC_CONTROL = "esp32/control"

# Shared variables for data storage
latest_data = {"x": None, "y": None, "speed": None, "distance": None}
status = "Connecting..."

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC_TARGET)
        client.subscribe(MQTT_TOPIC_STATUS)
    else:
        print("❌ Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
    global latest_data, status
    if msg.topic == MQTT_TOPIC_TARGET:
        try:
            payload = json.loads(msg.payload.decode())
            latest_data.update(payload)
        except Exception as e:
            print("Payload Error:", e)
    elif msg.topic == MQTT_TOPIC_STATUS:
        status = msg.payload.decode()

# MQTT Setup
def connect_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()  # Enable SSL/TLS
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    return client

mqtt_client = connect_mqtt()
mqtt_thread = threading.Thread(target=mqtt_client.loop_forever)
mqtt_thread.daemon = True
mqtt_thread.start()

# Streamlit UI
st.set_page_config(page_title="ESP32 Control Panel", layout="centered")
st.title("💡 ESP32 Control Panel")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔘 LED Control")
    if st.button("Turn ON"):
        mqtt_client.publish(MQTT_TOPIC_CONTROL, "ON")
    if st.button("Turn OFF"):
        mqtt_client.publish(MQTT_TOPIC_CONTROL, "OFF")
    st.markdown(f"**Status:** `{status}`")

def safe(val):
    return val if val is not None else "..."

with col2:
    st.markdown("### 📍 Target Info")
    st.metric(label="X", value=safe(latest_data["x"]))
    st.metric(label="Y", value=safe(latest_data["y"]))
    st.metric(label="Speed", value=safe(latest_data["speed"]))
    st.metric(label="Distance", value=safe(latest_data["distance"]))
