import time
import json
import mysql.connector
import paho.mqtt.client as mqtt
import ssl
from opcua import Client, ua

# --- ☁️ CONFIGURATION ---
BROKER = "af3003c0f9884d19872d4a753f3d2acd.s1.eu.hivemq.cloud"
PORT = 8883
USER = "abijith"
PASS = "Password123!"

PLC_URL = "opc.tcp://192.168.0.20:49320"
DATA_TOPIC = "factory/machine1/data"
CONTROL_TOPIC = "factory/machine1/control"
SETPOINT_TOPIC = "factory/machine1/setpoint"

# --- 🗄️ MYSQL CONNECTION SETUP ---
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Password123!", 
    "database": "factory_io",
    "auth_plugin": "mysql_native_password"  # This fixes the access denied error
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Initialize Database Table
try:
    print("🗄️ Connecting to MySQL Server...")
    init_db = get_db_connection()
    cursor = init_db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS machine_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cv INT,
            pv INT,
            motor_status BOOLEAN
        )
    """)
    init_db.commit()
    init_db.close()
    print("✅ MySQL Table Verified & Ready")
except Exception as e:
    print(f"❌ MySQL Init Error: {e}")
    exit()

# --- OPC UA Global Nodes ---
node_start_key = None
node_stop_key = None
node_pv = None

# --- MQTT CALLBACKS ---
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("☁️ HIVEMQ CLOUD ONLINE")
        client.subscribe([(CONTROL_TOPIC, 0), (SETPOINT_TOPIC, 0)])

def on_message(client, userdata, msg):
    global node_start_key, node_stop_key, node_pv
    payload = msg.payload.decode()
    try:
        if msg.topic == CONTROL_TOPIC:
            if payload == "START":
                node_start_key.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
            elif payload == "RELEASE_START":
                node_start_key.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
            elif payload == "STOP":
                node_stop_key.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
            elif payload == "RELEASE_STOP":
                node_stop_key.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
        elif msg.topic == SETPOINT_TOPIC:
            node_pv.set_value(ua.DataValue(ua.Variant(int(payload), ua.VariantType.Int16)))
    except Exception as e:
        print(f"❌ Control Error: {e}")

# --- INIT MQTT & OPC UA ---
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.username_pw_set(USER, PASS)
mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

opc_client = Client(PLC_URL)

try:
    print(f"🔌 Connecting to PLC...")
    opc_client.connect()
    
    node_start_key = opc_client.get_node("ns=2;s=DR.Device1.Symbol Set.START")
    node_stop_key = opc_client.get_node("ns=2;s=DR.Device1.Symbol Set.STOP")
    node_cv = opc_client.get_node("ns=2;s=DR.Device1.Symbol Set.CV")
    node_pv = opc_client.get_node("ns=2;s=DR.Device1.Symbol Set.PV")
    node_motor = opc_client.get_node("ns=2;s=DR.Device1.Symbol Set.MOTOR")

    print("🚀 SYSTEM READY - LOGGING TO MYSQL")

    # Persistent DB connection for the loop
    active_db = get_db_connection()
    db_cursor = active_db.cursor()

    while True:
        try:
            cv_val = node_cv.get_value()
            pv_val = node_pv.get_value()
            motor_state = node_motor.get_value()
            
            # 1. Publish to Cloud
            packet = {"cv": cv_val, "pv": pv_val, "motor_led": 1 if motor_state else 0}
            mqtt_client.publish(DATA_TOPIC, json.dumps(packet))
            
            # 2. Log to MySQL
            insert_query = "INSERT INTO machine_log (cv, pv, motor_status) VALUES (%s, %s, %s)"
            db_cursor.execute(insert_query, (cv_val, pv_val, motor_state))
            active_db.commit()
            
            print(f"📊 CV: {cv_val} | PV: {pv_val} | Logged to MySQL")
            time.sleep(1)
            
        except mysql.connector.Error:
            print("⚠️ DB Connection lost, reconnecting...")
            time.sleep(1)
            active_db = get_db_connection()
            db_cursor = active_db.cursor()
        except Exception as e:
            print(f"⚠️ Loop Error: {e}")
            time.sleep(2)

finally:
    mqtt_client.loop_stop()
    opc_client.disconnect()
    if 'active_db' in locals(): active_db.close()
