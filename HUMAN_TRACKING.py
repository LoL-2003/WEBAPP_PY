import streamlit as st
import paho.mqtt.client as mqtt
import queue
import threading

# Step 1: Initialize state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "mqtt_messages" not in st.session_state:
    st.session_state["mqtt_messages"] = []

mqtt_queue = queue.Queue()

# Step 2: Define MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe("esp32/target")

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    mqtt_queue.put(message)  # Use queue instead of session_state

# Step 3: Start MQTT in background
def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

# Step 4: Streamlit UI
st.title("MQTT Dashboard")

# Poll queue safely and update session state
while not mqtt_queue.empty():
    message = mqtt_queue.get()
    st.session_state["mqtt_messages"].append(message)

# Display messages
st.write("Received Messages:")
st.write(st.session_state["mqtt_messages"])
