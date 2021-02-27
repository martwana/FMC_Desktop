#! /usr/bin/env python3


import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
import json

class Server():

    AP_ALT_VAR_SET_ENGLISH = 10000
    AP_SPD_VAR_SET = 220
    HEADING_BUG_SET = 180
    COM_STANDBY_FREQUENCY = 122.800
    COM_ACTIVE_FREQUENCY = 134.850

    def __init__(self):
        self.init_mqtt()

    def init_mqtt(self):
        mqttBroker ="192.168.100.200" 
        self.mqttClient = mqtt.Client("PC")
        self.mqttClient.connect(mqttBroker) 

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload)
        for key in data.keys():
            self.processChange(key, data[key])

    def processChange(self, key, value):

        if key == "ALTITUDE":
            AP_ALT_VAR_SET_ENGLISH = value
        elif key == "SPEED":
            AP_SPD_VAR_SET = value
        elif key == "HEADING":
            HEADING_BUG_SET = value
        elif key == "RADIO_COM_1_STBY":
            pass

            if value['ACTION'] == "ADJUST":

                if value['SIDE'] == "LEFT":
                    if value['DIRECTION'] == "UP":
                        self.COM_STANDBY_FREQUENCY = self.COM_STANDBY_FREQUENCY + 1
                    else: 
                        self.COM_STANDBY_FREQUENCY = self.COM_STANDBY_FREQUENCY - 1
                elif value['SIDE'] == "RIGHT":
                    if value['DIRECTION'] == "UP":
                        self.COM_ACTIVE_FREQUENCY = self.COM_ACTIVE_FREQUENCY + 1
                    else: 
                        self.COM_ACTIVE_FREQUENCY = self.COM_ACTIVE_FREQUENCY - 1
            elif value['ACTION'] == "SWAP":
                self.aircraftEvents.find("COM_STBY_RADIO_SWAP")()
            
    
    def run(self):
        self.mqttClient.loop_start()

        self.mqttClient.subscribe("FS_DATA_IN")
        self.mqttClient.on_message=self.on_message 

        while True:
            try:
                stdby_freq = '{:.3f}'.format(round(float(self.COM_STANDBY_FREQUENCY), 3))
                active_freq = '{:.3f}'.format(round(float(self.COM_ACTIVE_FREQUENCY), 3))

                data = {
                    "RADIO_COM_1": {
                        "ACTIVE": active_freq,
                        "STANDBY": stdby_freq
                    },
                    "HEADING": '{:.0f}'.format(self.HEADING_BUG_SET),
                    "ALTITUDE": '{:.0f}'.format(self.AP_ALT_VAR_SET_ENGLISH),
                    "SPEED": '{:.0f}'.format(self.AP_SPD_VAR_SET)
                }
                self.mqttClient.publish("FS_DATA_OUT", json.dumps(data))

            except Exception as e:
                print(e)
        
        self.mqttClient.loop_stop()

server = Server()

server.run()


