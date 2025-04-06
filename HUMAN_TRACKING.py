import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import threading
import json
import time
from datetime import datetime

# MQTT Config
MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
MQTT_PORT = 8883
MQTT_USERNAME = "xaygsnkk:xaygsnkk"
MQTT_PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC_SUB = "esp32/target"

# Initialize Streamlit session state
if "mqtt_messages" not in st.session_state:
    st.session_state.mqtt_messages = []

# Callback: on connect
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    if rc == 0:
        client.subscribe(TOPIC_SUB)
    else:
        print("Failed to connect, return code:", rc)

# Callback: on message
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        msg_dict = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "x": data.get("x"),
            "y": data.get("y"),
            "speed": data.get("speed"),
            "distance": data.get("distance")
        }
        st.session_state.mqtt_messages.append(msg_dict)
        print("Message received:", msg_dict)
    except Exception as e:
        print("Error:", e)

# Thread function
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# Start MQTT client only once
if "mqtt_thread_started" not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_thread_started = True

# Streamlit UI
st.title("📡 ESP32 MQTT Data Dashboard")
st.subheader("📬 Received Data")

output = st.empty()

# Live refresh
while True:
    with output.container():
        if st.session_state.mqtt_messages:
            for msg in reversed(st.session_state.mqtt_messages[-10:]):
                st.markdown(f"""
                    - ⏱️ **Time**: {msg['time']}
                    - 📍 **X**: {msg['x']}, **Y**: {msg['y']}
                    - 🚀 **Speed**: {msg['speed']}
                    - 📏 **Distance**: {msg['distance']}
                    ---
                """)
        else:
            st.info("Waiting for MQTT messages...")
    time.sleep(1)
