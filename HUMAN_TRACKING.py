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
import threading
import json
import plotly.graph_objs as go

# MQTT Config
BROKER = "b1040f453c014b0fb5eeebc408edf63d.s1.eu.hivemq.cloud"
PORT = 8883
USERNAME = "HUMAN_TRACKING"
PASSWORD = "12345678aA"

CONTROL_TOPIC = "esp32/control"
STATUS_TOPIC = "esp32/status"
SENSOR_TOPIC = "esp32/target"

# Session state
if "mqtt_started" not in st.session_state:
    st.session_state.mqtt_started = False
if "status" not in st.session_state:
    st.session_state.status = "🔴 Offline"
if "data" not in st.session_state:
    st.session_state.data = {"x": [], "y": [], "speed": [], "distance": []}

# Streamlit UI
st.set_page_config(page_title="Human Tracking", layout="wide")
st.title("📡 Real-Time Human Tracking Dashboard")
st.markdown(f"### Status: {st.session_state.status}")
led_col1, led_col2 = st.columns(2)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(STATUS_TOPIC)
        client.subscribe(SENSOR_TOPIC)
        client.publish(STATUS_TOPIC, "ONLINE")
    else:
        st.session_state.status = f"❌ MQTT Connect Failed: {rc}"

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == STATUS_TOPIC:
        if "ONLINE" in payload:
            st.session_state.status = "🟢 Online"

    elif topic == SENSOR_TOPIC:
        try:
            data = json.loads(payload)
            for key in ["x", "y", "speed", "distance"]:
                if key in data:
                    st.session_state.data[key].append(data[key])
                    if len(st.session_state.data[key]) > 100:
                        st.session_state.data[key] = st.session_state.data[key][-100:]
        except Exception as e:
            print("Parse Error:", e)

# MQTT Thread Start
def start_mqtt():
    client = mqtt.Client()
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_forever()

if not st.session_state.mqtt_started:
    threading.Thread(target=start_mqtt, daemon=True).start()
    st.session_state.mqtt_started = True

# LED Controls
if led_col1.button("🔆 Turn ON"):
    pub = mqtt.Client()
    pub.username_pw_set(USERNAME, PASSWORD)
    pub.tls_set()
    pub.connect(BROKER, PORT)
    pub.publish(CONTROL_TOPIC, "ON")
    st.success("Sent: ON")

if led_col2.button("🌙 Turn OFF"):
    pub = mqtt.Client()
    pub.username_pw_set(USERNAME, PASSWORD)
    pub.tls_set()
    pub.connect(BROKER, PORT)
    pub.publish(CONTROL_TOPIC, "OFF")
    st.success("Sent: OFF")

# Combined Graph
st.subheader("📊 Distance, Speed and Position Graph")

fig = go.Figure()
fig.add_trace(go.Scatter(y=st.session_state.data["x"], mode='lines', name='X Position'))
fig.add_trace(go.Scatter(y=st.session_state.data["y"], mode='lines', name='Y Position'))
fig.add_trace(go.Scatter(y=st.session_state.data["speed"], mode='lines', name='Speed'))
fig.add_trace(go.Scatter(y=st.session_state.data["distance"], mode='lines', name='Distance'))

fig.update_layout(title="Human Movement Tracking",
                  xaxis_title="Time (samples)",
                  yaxis_title="Value",
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

st.plotly_chart(fig, use_container_width=True)

st.markdown("👨‍💻 Developed by **Aditya Puri**")
