import paho.mqtt.client as mqtt
import sqlite3
import json
from queue import Queue
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "messages.db")

message_queue = Queue()

def on_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    message_queue.put((topic, payload))

client = mqtt.Client()
client.on_message = on_message
client.connect("143.198.146.87", 1883)
client.subscribe("HIGrow/#")
client.loop_start()


while True:
    if not message_queue.empty():
        topic, payload = message_queue.get()

        data = json.loads(payload)
        plant_data = data['sensor']
        device_name = plant_data['HIGrow']
        date = plant_data['date']
        time = plant_data['time']
        temp = plant_data['temp']
        humid = plant_data['humid']
        soil = plant_data['soil']
        soil_temp = plant_data['soilTemp']
        salt = plant_data['salt']
        bat = plant_data['bat']
        batcharge = plant_data['batcharge']
        wifi_ssid = plant_data['wifissid']

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS messages (device_name text, date text, time text, temp real, humid real, soil real, soil_temp real, salt real, bat real, batcharge text, wifi_ssid text)''')
        cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (device_name, date, time, temp, humid, soil, soil_temp, salt, bat, batcharge, wifi_ssid))
        conn.commit()
        conn.close()
