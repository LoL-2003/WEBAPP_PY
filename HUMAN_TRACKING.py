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

# import streamlit as st
# import paho.mqtt.client as mqtt
# import json
# import base64
# import math
# import time
# import logging
# from datetime import datetime
# import os

# # Streamlit page configuration
# st.set_page_config(page_title="Real-Time Human Tracking", layout="wide")
# st.title("📡 Real-Time Human Tracking")
# st.markdown("Live data from ChirpStack MQTT")

# # MQTT Broker Configuration
# MQTT_SERVER_IP = "test.chirpstack.vandyam.com"
# MQTT_PORT = 1883
# APPLICATION_ID = "3ff2570b-20e9-4fbe-8519-2e0e880dc4f4"
# DEVICE_EUI = "c750f39bf0e894c7"
# TOPIC = f"application/{APPLICATION_ID}/device/{DEVICE_EUI}/event/#"

# # Frame structure constants
# HEADER = bytearray([0xAA, 0xFF, 0x03, 0x00])
# FOOTER = bytearray([0x55, 0xCC])
# NUM_TARGETS = 3
# CMD_SENSOR_DATA = 0xAB

# # Logging setup
# log_dir = "log"
# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)
# log_filename = f"mylog_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
# log_filename = os.path.join(log_dir, log_filename)
# logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.info("Streamlit MQTT target tracker started")

# # Global dictionary to track all targets
# target_data = {
#     1: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
#     2: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
#     3: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
# }

# # MQTT message processing
# def process_target_data(msg):
#     targets_found = 0
#     for i in range(NUM_TARGETS):
#         offset = 4 + (i * 8)  # Skip header (4 bytes)
#         x_raw = int.from_bytes(msg[offset:offset+2], byteorder='little')
#         y_raw = int.from_bytes(msg[offset+2:offset+4], byteorder='little')
#         speed_raw = int.from_bytes(msg[offset+4:offset+6], byteorder='little')
#         dist_raw = int.from_bytes(msg[offset+6:offset+8], byteorder='little')

#         # Apply formulas
#         x_coord = 0 - x_raw
#         y_coord = y_raw - 32768
#         speed = 0 - speed_raw
#         distance = dist_raw

#         # Calculate target distance
#         target_distance = math.sqrt(x_coord**2 + y_coord**2) / 10

#         # Handle special case for Y coordinate
#         if y_coord == -32768:
#             y_coord = 0

#         # Determine movement
#         movement = "Approaching" if speed < 0 else "Moving Away"
#         if speed == 0:
#             movement = "Stationary"

#         # Update target data if valid
#         if x_raw != 0 or y_raw != 0 or speed_raw != 0 or dist_raw != 0:
#             targets_found += 1
#             target_data[i+1]["x"] = x_coord / 10
#             target_data[i+1]["y"] = y_coord / 10
#             target_data[i+1]["speed"] = speed / 10
#             target_data[i+1]["distance"] = distance / 10
#             target_data[i+1]["movement"] = movement
#             target_data[i+1]["target_distance"] = target_distance
#             logging.info(f"Target {i+1} X Coordinate: {x_coord/10} cm")
#             logging.info(f"Target {i+1} Y Coordinate: {y_coord/10} cm")
#             logging.info(f"Target {i+1} Speed: {speed/10} cm/s ({movement})")
#             logging.info(f"Target {i+1} Distance Resolution: {distance/10} cm")
#             logging.info(f"Target {i+1} Distance: {target_distance:.2f} cm")

#     return targets_found

# # MQTT callbacks
# def on_connect(client, userdata, flags, rc):
#     st.success(f"Connected to MQTT broker with result code: {rc}")
#     client.subscribe(TOPIC)
#     logging.info(f"Subscribed to: {TOPIC}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         if msg.topic.endswith("/up"):
#             message = payload["data"]
#             message_bytes = base64.b64decode(message)
#             device_info = payload["deviceInfo"]
#             rssi = payload["rxInfo"][0].get("rssi", None)
#             snr = payload["rxInfo"][0].get("snr", None)
#             logging.info(f"Uplink from {device_info['deviceName']} Message: {hex(message_bytes[0])}")
#             logging.info(f"RSSI: {rssi} SNR: {snr}")
#             if message_bytes[0] == CMD_SENSOR_DATA and len(message_bytes) == 30 and message_bytes[:4] == HEADER and message_bytes[-2:] == FOOTER:
#                 logging.info("Detected Target Frame Structure")
#                 targets_found = process_target_data(message_bytes)
#                 logging.info(f"Found {targets_found} valid targets")
#             else:
#                 logging.info("Ignoring non-target frame")
#     except Exception as e:
#         st.error(f"Error processing message: {e}")
#         logging.error(f"Error processing message: {e}")

# # Setup MQTT client
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(MQTT_SERVER_IP, MQTT_PORT, 60)
# client.loop_start()

# # Streamlit layout
# col1, col2, col3 = st.columns(3)
# target_cols = [col1, col2, col3]

# placeholders = []
# for col, target_id in zip(target_cols, [1, 2, 3]):
#     col.subheader(f"🎯 Target {target_id}")
#     x = col.metric("X (cm)", "0.00")
#     y = col.metric("Y (cm)", "0.00")
#     speed = col.metric("Speed (cm/s)", "0.00")
#     dist = col.metric("Distance (cm)", "0.00")
#     movement = col.metric("Movement", "Stationary")
#     target_dist = col.metric("Target Distance (cm)", "0.00")
#     placeholders.append((x, y, speed, dist, movement, target_dist))

# # Main loop for updating Streamlit UI
# while True:
#     for i, (x_pl, y_pl, speed_pl, dist_pl, movement_pl, target_dist_pl) in enumerate(placeholders):
#         t_data = target_data[i + 1]
#         x_pl.metric("X (cm)", f"{t_data['x']:.2f}")
#         y_pl.metric("Y (cm)", f"{t_data['y']:.2f}")
#         speed_pl.metric("Speed (cm/s)", f"{t_data['speed']:.2f}")
#         dist_pl.metric("Distance (cm)", f"{t_data['distance']:.2f}")
#         movement_pl.metric("Movement", t_data['movement'])
#         target_dist_pl.metric("Target Distance (cm)", f"{t_data['target_distance']:.2f}")
#     time.sleep(0.5)


# import streamlit as st
# import paho.mqtt.client as mqtt
# import json
# import base64
# import math
# import time
# import logging
# from datetime import datetime
# import os
# import socket
# import errno

# # Streamlit page configuration
# st.set_page_config(page_title="Real-Time Human Tracking", layout="wide")
# st.title("📡 Real-Time Human Tracking")
# st.markdown("Live data from ChirpStack MQTT")

# # MQTT Broker Configuration
# MQTT_SERVER_IP = "test.chirpstack.vandyam.com"
# MQTT_PORT = 1883
# APPLICATION_ID = "3ff2570b-20e9-4fbe-8519-2e0e880dc4f4"
# DEVICE_EUI = "c750f39bf0e894c7"
# TOPIC = f"application/{APPLICATION_ID}/device/{DEVICE_EUI}/event/#"

# # Frame structure constants
# HEADER = bytearray([0xAA, 0xFF, 0x03, 0x00])
# FOOTER = bytearray([0x55, 0xCC])
# NUM_TARGETS = 3

# # Logging setup
# log_dir = "log"
# if not os.path.exists(log_dir):
#     os.makedirs(log_dir)
# log_filename = f"mylog_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
# log_filename = os.path.join(log_dir, log_filename)
# logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.info("Streamlit MQTT target tracker started")

# # Global dictionary to track all targets
# target_data = {
#     1: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
#     2: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
#     3: {"x": 0, "y": 0, "speed": 0, "distance": 0, "movement": "Stationary", "target_distance": 0},
# }

# # MQTT message processing
# def process_target_data(msg):
#     targets_found = 0
#     for i in range(NUM_TARGETS):
#         offset = 4 + (i * 8)  # Skip header (4 bytes)
#         x_raw = int.from_bytes(msg[offset:offset+2], byteorder='little')
#         y_raw = int.from_bytes(msg[offset+2:offset+4], byteorder='little')
#         speed_raw = int.from_bytes(msg[offset+4:offset+6], byteorder='little')
#         dist_raw = int.from_bytes(msg[offset+6:offset+8], byteorder='little')

#         # Apply formulas
#         x_coord = 0 - x_raw
#         y_coord = y_raw - 32768
#         speed = 0 - speed_raw
#         distance = dist_raw

#         # Calculate target distance
#         target_distance = math.sqrt(x_coord**2 + y_coord**2) / 10

#         # Handle special case for Y coordinate
#         if y_coord == -32768:
#             y_coord = 0

#         # Determine movement
#         movement = "Approaching" if speed < 0 else "Moving Away"
#         if speed == 0:
#             movement = "Stationary"

#         # Update target data if valid
#         if x_raw != 0 or y_raw != 0 or speed_raw != 0 or dist_raw != 0:
#             targets_found += 1
#             target_data[i+1]["x"] = x_coord / 10
#             target_data[i+1]["y"] = y_coord / 10
#             target_data[i+1]["speed"] = speed / 10
#             target_data[i+1]["distance"] = distance / 10
#             target_data[i+1]["movement"] = movement
#             target_data[i+1]["target_distance"] = target_distance
#             logging.info(f"Target {i+1} X Coordinate: {x_coord/10} cm")
#             logging.info(f"Target {i+1} Y Coordinate: {y_coord/10} cm")
#             logging.info(f"Target {i+1} Speed: {speed/10} cm/s ({movement})")
#             logging.info(f"Target {i+1} Distance Resolution: {distance/10} cm")
#             logging.info(f"Target {i+1} Distance: {target_distance:.2f} cm")

#     return targets_found

# # MQTT callbacks
# def on_connect(client, userdata, flags, rc):
#     st.success(f"Connected to MQTT broker with result code: {rc}")
#     client.subscribe(TOPIC)
#     logging.info(f"Subscribed to: {TOPIC}")

# def on_disconnect(client, userdata, rc):
#     if rc != 0:
#         st.error(f"Disconnected from MQTT broker unexpectedly with result code: {rc}")
#     else:
#         st.warning("Disconnected from MQTT broker")
#     logging.info(f"Disconnected from MQTT broker with result code: {rc}")

# def on_message(client, userdata, msg):
#     try:
#         payload = json.loads(msg.payload.decode())
#         if msg.topic.endswith("/up"):
#             message = payload["data"]
#             message_bytes = base64.b64decode(message)
#             device_info = payload["deviceInfo"]
#             rssi = payload["rxInfo"][0].get("rssi", None)
#             snr = payload["rxInfo"][0].get("snr", None)
#             logging.info(f"Uplink from {device_info['deviceName']} Message: {hex(message_bytes[0])}")
#             logging.info(f"Raw message (hex): {message_bytes.hex()}")
#             logging.info(f"RSSI: {rssi} SNR: {snr}")
#             if len(message_bytes) == 30 and message_bytes[:4] == HEADER and message_bytes[-2:] == FOOTER:
#                 logging.info("Detected Target Frame Structure")
#                 targets_found = process_target_data(message_bytes)
#                 logging.info(f"Found {targets_found} valid targets")
#             else:
#                 logging.info("Ignoring non-target frame")
#     except Exception as e:
#         st.error(f"Error processing message: {e}")
#         logging.error(f"Error processing message: {e}")

# # Function to connect with retries
# def connect_mqtt(client, max_retries=5, delay=5):
#     attempt = 0
#     while attempt < max_retries:
#         try:
#             client.connect(MQTT_SERVER_IP, MQTT_PORT, 60)
#             return True
#         except socket.gaierror as e:
#             st.error(f"DNS resolution failed for {MQTT_SERVER_IP}: {e}")
#             logging.error(f"DNS resolution failed: {e}")
#         except socket.timeout as e:
#             st.error(f"Connection timed out to {MQTT_SERVER_IP}:{MQTT_PORT}: {e}")
#             logging.error(f"Connection timeout: {e}")
#         except socket.error as e:
#             if e.errno == errno.ECONNREFUSED:
#                 st.error(f"Connection refused by {MQTT_SERVER_IP}:{MQTT_PORT}: {e}")
#                 logging.error(f"Connection refused: {e}")
#             else:
#                 st.error(f"Socket error connecting to {MQTT_SERVER_IP}:{MQTT_PORT}: {e}")
#                 logging.error(f"Socket error: {e}")
#         attempt += 1
#         if attempt < max_retries:
#             st.warning(f"Retry {attempt + 1}/{max_retries} in {delay} seconds...")
#             logging.info(f"Retry {attempt + 1}/{max_retries} in {delay} seconds")
#             time.sleep(delay)
#     st.error("Failed to connect to MQTT broker after maximum retries.")
#     logging.error("Failed to connect to MQTT broker after maximum retries")
#     return False

# # Setup MQTT client
# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_disconnect = on_disconnect
# client.on_message = on_message

# # Attempt to connect
# if connect_mqtt(client):
#     client.loop_start()

# # Streamlit layout
# col1, col2, col3 = st.columns(3)
# target_cols = [col1, col2, col3]

# placeholders = []
# for col, target_id in zip(target_cols, [1, 2, 3]):
#     col.subheader(f"🎯 Target {target_id}")
#     x = col.metric("X (cm)", "0.00")
#     y = col.metric("Y (cm)", "0.00")
#     speed = col.metric("Speed (cm/s)", "0.00")
#     dist = col.metric("Distance (cm)", "0.00")
#     movement = col.metric("Movement", "Stationary")
#     target_dist = col.metric("Target Distance (cm)", "0.00")
#     placeholders.append((x, y, speed, dist, movement, target_dist))

# # Main loop for updating Streamlit UI
# while True:
#     for i, (x_pl, y_pl, speed_pl, dist_pl, movement_pl, target_dist_pl) in enumerate(placeholders):
#         t_data = target_data[i + 1]
#         x_pl.metric("X (cm)", f"{t_data['x']:.2f}")
#         y_pl.metric("Y (cm)", f"{t_data['y']:.2f}")
#         speed_pl.metric("Speed (cm/s)", f"{t_data['speed']:.2f}")
#         dist_pl.metric("Distance (cm)", f"{t_data['distance']:.2f}")
#         movement_pl.metric("Movement", t_data['movement'])
#         target_dist_pl.metric("Target Distance (cm)", f"{t_data['target_distance']:.2f}")
#     time.sleep(0.5)
