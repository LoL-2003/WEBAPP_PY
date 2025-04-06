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

CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"
TARGET_TOPIC = "esp32/target"

# Initialize session state
if "status" not in st.session_state:
    st.session_state["status"] = "Connecting..."

if "data" not in st.session_state:
    st.session_state["data"] = {"x": None, "y": None, "speed": None, "distance": None}

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT Connected")
        client.subscribe(STATUS_TOPIC)
        client.subscribe(TARGET_TOPIC)
    else:
        print(f"❌ MQTT connection failed: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    if msg.topic == STATUS_TOPIC:
        st.session_state["status"] = payload
    elif msg.topic == TARGET_TOPIC:
        try:
            json_data = json.loads(payload)
            st.session_state["data"].update(json_data)
        except Exception as e:
            print("⚠️ Error decoding target data:", e)

# Start MQTT client thread
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()

if "mqtt_thread_started" not in st.session_state:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state["mqtt_thread_started"] = True

# Streamlit UI
st.set_page_config(page_title="ESP32 Control Panel", page_icon="📟", layout="centered")
st.title("📟 ESP32 Control Panel")

col1, col2 = st.columns(2)

# Status + Controls
with col1:
    st.markdown("### 🔘 Device Control")
    st.markdown(f"**Status:** `{st.session_state['status']}`")
    
    led_icon = "🟢" if st.session_state["status"].upper() == "ON" else "🔴"
    st.markdown(f"<h1 style='text-align: center;'>{led_icon}</h1>", unsafe_allow_html=True)

    if st.button("Turn ON"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "ON")
        st.success("Turn ON command sent")

    if st.button("Turn OFF"):
        pub = mqtt.Client()
        pub.username_pw_set(USERNAME, PASSWORD)
        pub.tls_set()
        pub.connect(BROKER, PORT)
        pub.publish(CONTROL_TOPIC, "OFF")
        st.success("Turn OFF command sent")

# Live Sensor Data
def show(val):
    return val if val is not None else "..."

with col2:
    st.markdown("### 📍 Sensor Data")
    st.metric("X", show(st.session_state["data"].get("x")))
    st.metric("Y", show(st.session_state["data"].get("y")))
    st.metric("Speed", show(st.session_state["data"].get("speed")))
    st.metric("Distance", show(st.session_state["data"].get("distance")))

st.markdown("---")
st.markdown("👨‍💻 Developed by **Aditya Puri** 🚀")
