#! /usr/bin/env python3

import Interface
import EncoderSet
import MQTT_Client
import json

from time import sleep

class FMC_Desktop():

    ALTITUDE_STEPS = 1000
    RADIO_ACTIVE_SEG = "RIGHT"

    def __init__(self, config):
        self.config = config

        self.interface = Interface.Interface(self, config['lcd_address'])
        self.encoders = EncoderSet.EncoderSet(self, config['encoders'])
        self.mqtt = MQTT_Client.MQTT_Client(self, config['mqtt'])

    def update_value(self, encoder, value):
        current_menu = self.interface.get_menu_item_key()
        if current_menu == "RADIO_COM_1":
            pass
        else: 
            self.interface.VALUES[self.interface.MENU_ITEMS[current_menu]['variable']] = value
            data = {
                self.interface.MENU_ITEMS[current_menu]['variable']: value
            }
            self.mqtt.client.publish("FS_DATA_IN", json.dumps(data))

    def get_current_value(self):
        current_menu = self.interface.get_menu_item_key()
        if current_menu == "RADIO_COM_1":
            return self.interface.VALUES[self.interface.MENU_ITEMS[current_menu][f'variable_{self.RADIO_ACTIVE_SEG.lower()}']]
        else: 
            return self.interface.VALUES[self.interface.MENU_ITEMS[current_menu]['variable']]

        return 0

    def double_button_press(self):
        if self.interface.get_menu_item_key() == "RADIO_COM_1":
            data = {
                "RADIO_COM_1_STBY": {
                    "ACTION": "SWAP"
                }
            }
            self.mqtt.client.publish("FS_DATA_IN", json.dumps(data))

    def increment_value(self):
        if self.interface.get_menu_item_key() == "RADIO_COM_1":
            self.send_radio_update("UP")
        

    def decrement_value(self):
        if self.interface.get_menu_item_key() == "RADIO_COM_1":
            self.send_radio_update("DOWN")

    def send_radio_update(self, direction):
        if self.interface.get_menu_item_key() == "RADIO_COM_1":
            data = {
                "RADIO_COM_1_STBY": {
                    "ACTION": "ADJUST",
                    "SIDE": self.RADIO_ACTIVE_SEG,
                    "DIRECTION": direction
                }
            }
            self.mqtt.client.publish("FS_DATA_IN", json.dumps(data))

    def button_press(self):
        if self.interface.get_menu_item_key() == "ALTITUDE":
            if self.ALTITUDE_STEPS == 100:
                self.ALTITUDE_STEPS = 1000
            else:
                self.ALTITUDE_STEPS = 100

            self.encoders.encoders['value'].set_encoder_config(self.get_encoder_definition())

        elif self.interface.get_menu_item_key() == "RADIO_COM_1":
            if self.RADIO_ACTIVE_SEG == "LEFT":
                self.RADIO_ACTIVE_SEG = "RIGHT"
            else:
                self.RADIO_ACTIVE_SEG = "LEFT"
        
            self.encoders.encoders['value'].set_encoder_config(self.get_encoder_definition())

    def get_altitude_steps(self):
        return self.ALTITUDE_STEPS

    def get_encoder_definition(self):

        encoder_definitions = {
            "ALTITUDE": {
                "step": self.get_altitude_steps(),
                "min": 0,
                "max": 42000,
                "color": 0x111111
            },
            "HEADING": {
                "step": 1,
                "min": 0,
                "max": 359,
                "color": 0x00FF00
            },
            "SPEED": {
                "step": 1,
                "min": 0,
                "max": 400,
                "color": 0x0000FF
            },
            "RADIO_COM_1_LEFT": {
                "step": 1,
                "min": 0,
                "max": 1,
                "color": 0x0f0f0f
            },
            "RADIO_COM_1_RIGHT": {
                "step": 1,
                "min": 0,
                "max": 1,
                "color": 0xFF0022
            }
        }

        key = self.interface.get_menu_item_key()

        if key == "RADIO_COM_1":
            key = f'{key}_{self.RADIO_ACTIVE_SEG}'

        return encoder_definitions[key]


    def run(self):
        print("starting")
        self.interface.clear()
        while True:
            self.interface.show()


config = {
    'lcd_address': 0x27,
    'encoders': {
        "interrupt_pin": 4,
        "device_mapping": [
            {
                'name': "menu",
                'address': 0x50,
            },
            {
                'name': "value",
                'address': 0x40,
            }
        ]
    },
    'mqtt': {
        'broker': "localhost",
        "client_name": "FMC_Desktop"
    }
}

fmc = FMC_Desktop(config)

fmc.run()