#! /usr/bin/env python3


import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
import json
from SimConnect import *


class Server():

    SEND = False

    ALTITUDE = 0
    SPEED = 0
    HEADING = 0
    RADIO_COM_1 = 0

    def __init__(self):
        self.init_mqtt()
        self.init_simconnect()

    def init_simconnect(self):
        self.sc = SimConnect()
        self.aircraftReqs = AircraftRequests(self.sc, _time=2000)
        self.aircraftEvents = AircraftEvents(self.sc)

    def init_mqtt(self):
        mqttBroker ="192.168.100.148" 
        self.mqttClient = mqtt.Client("PC")
        self.mqttClient.connect(mqttBroker) 

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload)

        for key in data.keys():
            self.processChange(key, data[key])


    def processChange(self, key, value):

        if key == "ALTITUDE":
            self.ALTITUDE = value
            self.aircraftEvents.find("AP_ALT_VAR_SET_ENGLISH")(self.ALTITUDE)  # Sets AP autopilot hold level
        elif key == "SPEED":
            self.SPEED = value
            self.aircraftEvents.find("AP_SPD_VAR_SET")(self.SPEED)
        elif key == "HEADING":
            self.HEADING = value
            self.aircraftEvents.find("HEADING_BUG_SET")(self.HEADING)
        elif key == "RADIO_COM_1":
            self.RADIO_COM_1 = value
            self.aircraftEvents.find("COM_STBY_RADIO_SET")(self.RADIO_COM_1)

            # KEY_FREQUENCY_SWAP

    
    def run(self):
        self.mqttClient.loop_start()

        self.mqttClient.subscribe("FS_DATA_IN")
        self.mqttClient.on_message=self.on_message 

        while True:

            # if self.SEND:
            #     data = {
            #         "speed": "123",
            #         "altitude": self.ALTITUDE,
            #         "heading": "222"
            #     }
            #     self.mqttClient.publish("FS_DATA_OUT", json.dumps(data))
            #     print("Just published " + json.dumps(data) + " to topic FS_DATA_OUT")
            #     self.SEND = False
            time.sleep(1)

        
        self.mqttClient.loop_stop()

server = Server()

server.run()


