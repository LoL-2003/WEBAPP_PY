import streamlit as st
import paho.mqtt.client as mqtt
import threading
import json
import ssl

# MQTT Configuration
BROKER = "chameleon.lmq.cloudamqp.com"
PORT = 8883
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"

CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"
TARGET_TOPIC = "esp32/target"

# Shared state
status = st.session_state.get("status", "Connecting...")
data = st.session_state.get("data", {"x": None, "y": None, "speed": None, "distance": None})

# Streamlit UI
st.set_page_config(page_title="ESP32 Control Panel", page_icon="💡", layout="centered")
st.title("💡 ESP32 Control Panel")

col1, col2 = st.columns(2)
status_placeholder = col1.empty()
status_placeholder.markdown(f"**Status:** `{status}`")

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(STATUS_TOPIC)
        client.subscribe(TARGET_TOPIC)
    else:
        print(f"MQTT Connection failed with code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if msg.topic == STATUS_TOPIC:
        st.session_state["status"] = payload
    elif msg.topic == TARGET_TOPIC:
        try:
            json_data = json.loads(payload)
            st.session_state["data"] = json_data
        except Exception as e:
            print(f"Error decoding message: {e}")

# MQTT Thread
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

# Run MQTT only once
if "mqtt_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_started"] = True

# LED Control Section
with col1:
    st.markdown("### 🔘 LED Control")
    led_color = "🟢" if st.session_state.get("status") == "ON" else "🔴"
    st.markdown(f"<div style='font-size:48px;'>{led_color}</div>", unsafe_allow_html=True)

    if st.button("Turn ON"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "ON")
        st.success("Sent 'ON' command")

    if st.button("Turn OFF"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "OFF")
        st.success("Sent 'OFF' command")

# Target Sensor Data
def show_val(v): return v if v is not None else "..."

with col2:
    st.markdown("### 📍 Target Data")
    st.metric("X", show_val(st.session_state["data"].get("x")))
    st.metric("Y", show_val(st.session_state["data"].get("y")))
    st.metric("Speed", show_val(st.session_state["data"].get("speed")))
    st.metric("Distance", show_val(st.session_state["data"].get("distance")))

st.markdown("---")
st.markdown("👨‍💻 Developed by **Aditya Puri** 🚀")
