import paho.mqtt.client as mqtt
import ssl
import json
import time

# HiveMQ Cloud Credentials (same as ESP32)
BROKER = "chameleon.lmq.cloudamqp.com"
PORT = 8883  # TLS port
USERNAME = "xaygsnkk:xaygsnkk"
PASSWORD = "mOLBh4PE5GW_Vd7I4TMQ-eMc02SvIrbS"
TOPIC = "esp32/target"

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker securely!")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Failed to connect, return code {rc}")

# Callback when a message is received
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        x = data.get("x")
        y = data.get("y")
        speed = data.get("speed")
        distance = data.get("distance")
        print(f"📍 Target => X: {x}, Y: {y}, Speed: {speed}, Distance: {distance}")
    except Exception as e:
        print(f"⚠️ Error decoding message: {e}")

# MQTT Client Setup (v3.1.1 to avoid deprecation)
client = mqtt.Client(protocol=mqtt.MQTTv311)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Configure TLS (secure, but no certificate verification)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)

# Connect and loop
client.connect(BROKER, PORT, keepalive=60)
client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("👋 Exiting...")
    client.loop_stop()
    client.disconnect()
