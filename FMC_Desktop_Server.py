#! /usr/bin/env python3


import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
import json
from SimConnect import *

class Server():

    def __init__(self):
        self.init_mqtt()
        self.init_simconnect()

    def init_simconnect(self):
        self.sc = SimConnect()
        self.aircraftReqs = AircraftRequests(self.sc, _time=0)
        self.aircraftEvents = AircraftEvents(self.sc)

    def init_mqtt(self):
        mqttBroker ="192.168.100.148" 
        self.mqttClient = mqtt.Client("PC")
        self.mqttClient.connect(mqttBroker) 

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload)
        for key in data.keys():
            self.processChange(key, data[key])

    def updateByEvent(self, event_name, new_value):
        event = self.aircraftEvents.find(event_name)
        event(new_value)

    def processChange(self, key, value):

        if key == "ALTITUDE":
            self.updateByEvent("AP_ALT_VAR_SET_ENGLISH", value)  # Sets AP autopilot hold level
        elif key == "SPEED":
            self.updateByEvent("AP_SPD_VAR_SET", value)
        elif key == "HEADING":
            self.updateByEvent("HEADING_BUG_SET", value)
        elif key == "RADIO_COM_1_STBY":

            if value['ACTION'] == "ADJUST":

                if value['SIDE'] == "LEFT":
                    if value['DIRECTION'] == "UP":
                        self.aircraftEvents.find("COM_RADIO_WHOLE_INC")()
                    else: 
                        self.aircraftEvents.find("COM_RADIO_WHOLE_DEC")()
                elif value['SIDE'] == "RIGHT":
                    if value['DIRECTION'] == "UP":
                        self.aircraftEvents.find("COM_RADIO_FRACT_INC")()
                    else: 
                        self.aircraftEvents.find("COM_RADIO_FRACT_DEC")()
            elif value['ACTION'] == "SWAP":
                self.aircraftEvents.find("COM_STBY_RADIO_SWAP")()
            
    
    def run(self):
        self.mqttClient.loop_start()

        self.mqttClient.subscribe("FS_DATA_IN")
        self.mqttClient.on_message=self.on_message 

        while True:
            try:
                stdby_freq = '{:.3f}'.format(round(float(self.aircraftReqs.get("COM_STANDBY_FREQUENCY:1")), 3))
                active_freq = '{:.3f}'.format(round(float(self.aircraftReqs.get("COM_ACTIVE_FREQUENCY:1")), 3))

                data = {
                    "RADIO_COM_1": {
                        "ACTIVE": active_freq,
                        "STANDBY": stdby_freq
                    },
                    "HEADING": '{:.0f}'.format(self.aircraftReqs.get("AUTOPILOT_HEADING_LOCK_DIR")),
                    "ALTITUDE": '{:.0f}'.format(self.aircraftReqs.get("AUTOPILOT_ALTITUDE_LOCK_VAR")),
                    "SPEED": '{:.0f}'.format(self.aircraftReqs.get("AUTOPILOT_AIRSPEED_HOLD_VAR"))
                }
                self.mqttClient.publish("FS_DATA_OUT", json.dumps(data))
            except Exception as e:
                print(e)
        
        self.mqttClient.loop_stop()

server = Server()

server.run()


