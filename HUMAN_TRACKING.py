# import streamlit as st
# import paho.mqtt.client as mqtt
# import json
# import time
# import math

# st.set_page_config(page_title="Real-Time Human Tracking", layout="centered")
# st.title("📡 Real-Time Human Tracking")
# st.markdown("Live data from ESP32 via MQTT")

# # # MQTT Credentials
# # MQTT_BROKER = "chameleon.lmq.cloudamqp.com"
# # MQTT_PORT = 8883
# # USERNAME = "xaygsnkk:xaygsnkk"
# # PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
# TOPIC = "esp32/target"


# MQTT_BROKER = "fuji.lmq.cloudamqp.com"
# MQTT_PORT = 8883
# USERNAME = "qthbfpde:qthbfpde"
# PASSWORD = "Ct9dJehfPVqpIS6m0ZjDgVOgG-3EunYP"

# # Initialize values
# x, y, speed, distance = 0.0, 0.0, 0.0, 0.0
# prev_x, prev_y, prev_time = None, None, time.time()

# # MQTT callback
# def on_message(client, userdata, msg):
#     global x, y, speed, distance, prev_x, prev_y, prev_time
#     try:
#         payload = json.loads(msg.payload.decode())
#         new_x = float(payload.get("x", 0))
#         new_y = float(payload.get("y", 0))
#         curr_time = time.time()

#         # Calculate distance and speed
#         if prev_x is not None and prev_y is not None:
#             dx = new_x - prev_x
#             dy = new_y - prev_y
#             dt = max(curr_time - prev_time, 0.01)
#             distance = math.sqrt(dx**2 + dy**2)
#             speed = distance / dt

#         x, y = new_x, new_y
#         prev_x, prev_y = new_x, new_y
#         prev_time = curr_time

#     except Exception as e:
#         st.error(f"Error decoding message: {e}")

# # MQTT setup
# client = mqtt.Client()
# client.username_pw_set(USERNAME, PASSWORD)
# client.tls_set()
# client.on_message = on_message
# client.connect(MQTT_BROKER, MQTT_PORT, 60)
# client.subscribe(TOPIC)
# client.loop_start()

# # Display layout
# col1, col2, col3, col4 = st.columns(4)
# x_placeholder = col1.metric("X", "0.00")
# y_placeholder = col2.metric("Y", "0.00")
# speed_placeholder = col3.metric("Speed", "0.00 mm/s")
# distance_placeholder = col4.metric("Distance", "0.00 mm")

# # Live update loop
# while True:
#     x_placeholder.metric("X", f"{x:.2f}")
#     y_placeholder.metric("Y", f"{y:.2f}")
#     speed_placeholder.metric("Speed", f"{speed:.2f} units/s")
#     distance_placeholder.metric("Distance", f"{distance:.2f} units")
#     time.sleep(0.5)


import streamlit as st
import paho.mqtt.client as mqtt
import json
import time

st.set_page_config(page_title="Real-Time Human Tracking", layout="wide")
st.title("📡 Real-Time Human Tracking")
st.markdown("Live data from ESP32 via MQTT")

# MQTT Broker Credentials
MQTT_BROKER = "fuji.lmq.cloudamqp.com"
MQTT_PORT = 8883
USERNAME = "qthbfpde:qthbfpde"
PASSWORD = "Ct9dJehfPVqpIS6m0ZjDgVOgG-3EunYP"
TOPIC = "esp32/target"

# Global dictionary to track all targets
target_data = {
    1: {"x": 0, "y": 0, "speed": 0, "distance": 0},
    2: {"x": 0, "y": 0, "speed": 0, "distance": 0},
    3: {"x": 0, "y": 0, "speed": 0, "distance": 0},
}

# MQTT message handler
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        target_id = payload.get("target")
        if target_id in target_data:
            target_data[target_id]["x"] = payload.get("x", 0)
            target_data[target_id]["y"] = payload.get("y", 0)
            target_data[target_id]["speed"] = payload.get("speed", 0)
            target_data[target_id]["distance"] = payload.get("distance", 0)
    except Exception as e:
        st.error(f"Error decoding message: {e}")

# Setup MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set()
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(TOPIC)
client.loop_start()

# Placeholders for each target
col1, col2, col3 = st.columns(3)
target_cols = [col1, col2, col3]

placeholders = []
for col, target_id in zip(target_cols, [1, 2, 3]):
    col.subheader(f"🎯 Target {target_id}")
    x = col.metric("X (cm)", "0.00")
    y = col.metric("Y (cm)", "0.00")
    speed = col.metric("Speed (cm/s)", "0.00")
    dist = col.metric("Distance (cm)", "0.00")
    placeholders.append((x, y, speed, dist))

# Main loop
while True:
    for i, (x_pl, y_pl, speed_pl, dist_pl) in enumerate(placeholders):
        t_data = target_data[i + 1]
        x_pl.metric("X (cm)", f"{t_data['x']:.2f}")
        y_pl.metric("Y (cm)", f"{t_data['y']:.2f}")
        speed_pl.metric("Speed (cm/s)", f"{t_data['speed']:.2f}")
        dist_pl.metric("Distance (cm)", f"{t_data['distance']:.2f}")
    time.sleep(0.5)

