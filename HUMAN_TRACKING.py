import streamlit as st
import paho.mqtt.client as mqtt
import threading
import json
import ssl

# MQTT Config
BROKER = "chameleon.lmq.cloudamqp.com"
PORT = 8883
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC_SUB = "esp32/target"

# Initialize session state
if "mqtt_data" not in st.session_state:
    st.session_state.mqtt_data = {"x": "...", "y": "...", "speed": "...", "distance": "..."}

# Callback when message is received
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        st.session_state.mqtt_data = {
            "x": data.get("x", "..."),
            "y": data.get("y", "..."),
            "speed": data.get("speed", "..."),
            "distance": data.get("distance", "...")
        }
        st.experimental_rerun()
    except Exception as e:
        print("Error decoding message:", e)

# MQTT background thread
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = lambda client, userdata, flags, rc: client.subscribe(TOPIC_SUB)
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

# Start thread once
if "mqtt_thread_started" not in st.session_state:
    threading.Thread(target=mqtt_thread, daemon=True).start()
    st.session_state.mqtt_thread_started = True

# Streamlit UI
st.title("📡 Sensor Data Dashboard")
st.metric("X", st.session_state.mqtt_data["x"])
st.metric("Y", st.session_state.mqtt_data["y"])
st.metric("Speed", st.session_state.mqtt_data["speed"])
st.metric("Distance", st.session_state.mqtt_data["distance"])

st.markdown("---")
st.markdown("👨‍💻 Developed by **Aditya Puri** 🚀")
