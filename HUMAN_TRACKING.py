import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import json
import time
from datetime import datetime

# MQTT Broker settings
MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
MQTT_PORT = 8883
MQTT_USERNAME = "xaygsnkk:xaygsnkk"
MQTT_PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC_SUB = "esp32/target"

# Shared message store
if "messages" not in st.session_state:
    st.session_state.messages = []

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(TOPIC_SUB)
    else:
        st.error(f"Failed to connect: Code {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        timestamp = datetime.now().strftime("%H:%M:%S")
        message = {
            "timestamp": timestamp,
            "x": data.get("x", "N/A"),
            "y": data.get("y", "N/A"),
            "speed": data.get("speed", "N/A"),
            "distance": data.get("distance", "N/A")
        }
        st.session_state.messages.append(message)
        if len(st.session_state.messages) > 10:
            st.session_state.messages.pop(0)
    except Exception as e:
        print("Error parsing message:", e)

# Initialize MQTT once
@st.cache_resource
def init_mqtt():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    return client

# Start MQTT client
init_mqtt()

# Streamlit UI
st.title("📡 ESP32 MQTT Data Dashboard")
st.subheader("📬 Received Data")

container = st.empty()

# Live update loop
for _ in range(200):  # Refresh ~200 times (~20s)
    with container.container():
        if st.session_state.messages:
            for msg in reversed(st.session_state.messages):
                with st.expander(f"Message at {msg['timestamp']}"):
                    st.write(f"**X**: {msg['x']}")
                    st.write(f"**Y**: {msg['y']}")
                    st.write(f"**Speed**: {msg['speed']}")
                    st.write(f"**Distance**: {msg['distance']}")
        else:
            st.info("Waiting for MQTT messages...")
    time.sleep(0.1)
