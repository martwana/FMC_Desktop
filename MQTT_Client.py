#! /usr/bin/env python3

import paho.mqtt.client as mqtt
import json 

class MQTT_Client():

    def __init__(self, FMC, config):

        self.FMC = FMC
        self.config = config

        self.client = mqtt.Client(self.config['client_name'])
        self.client.connect(self.config['broker']) 

        self.client.subscribe("FS_DATA_OUT")
        self.client.on_message=self.on_message 

        self.client.loop_start()

    def on_message(self, client, userdata, message):
        data = json.loads(message.payload)
        try: 
            if data['RADIO_COM_1']:
                self.FMC.interface.VALUES['RADIO_COM_1_ACTIVE'] = data['RADIO_COM_1']['ACTIVE']
                parts = data['RADIO_COM_1']['STANDBY'].split('.')

                if parts:
                    left = parts[0]
                    right = parts[1]
                    self.FMC.interface.VALUES['RADIO_COM_1_STBY_LEFT'] = left
                    self.FMC.interface.VALUES['RADIO_COM_1_STBY_RIGHT'] = right.ljust(3, "0")

            if data['HEADING']:
                self.FMC.interface.VALUES['HEADING'] = data['HEADING']

            if data['ALTITUDE']:
                self.FMC.interface.VALUES['ALTITUDE'] = data['ALTITUDE']

            if data['SPEED']:
                self.FMC.interface.VALUES['SPEED'] = data['SPEED']

        except Exception as e:
            print(e)