import streamlit as st
import paho.mqtt.client as mqtt
import ssl
import json
from datetime import datetime

# MQTT Broker settings
MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
MQTT_PORT = 8883
MQTT_USERNAME = "xaygsnkk:xaygsnkk"
MQTT_PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC_SUB = "esp32/target"

# Global variables
client = None
received_messages = []

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
        received_messages.append(message)
        if len(received_messages) > 10:
            received_messages.pop(0)
        st.session_state.messages = received_messages.copy()
    except Exception as e:
        st.error(f"Error parsing message: {str(e)}")

# MQTT client initialization
def init_mqtt():
    global client
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    client.tls_insecure_set(False)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()  # No need for manual thread

# Streamlit UI
def main():
    st.title("📡 ESP32 MQTT Data Dashboard")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if client is None:
        init_mqtt()

    st.subheader("📬 Received Data")
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages):
            with st.expander(f"Message at {msg['timestamp']}"):
                st.write(f"**X**: {msg['x']}")
                st.write(f"**Y**: {msg['y']}")
                st.write(f"**Speed**: {msg['speed']}")
                st.write(f"**Distance**: {msg['distance']}")
    else:
        st.info("Waiting for MQTT messages...")

if __name__ == "__main__":
    main()
