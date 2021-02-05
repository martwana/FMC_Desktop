#! /usr/bin/env python3

import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

mqttBroker ="localhost"

client = mqtt.Client("Pi")
client.connect(mqttBroker) 

client.loop_start()

client.subscribe("TEMPERATURE")
client.on_message=on_message 

time.sleep(30)
client.loop_stop()