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

        self.interface = Interface.Interface(self, config)
        self.encoders = EncoderSet.EncoderSet(self, config['encoders'])
        self.mqtt = MQTT_Client.MQTT_Client(self, config['mqtt'])

    def update_value(self, encoder, value):
        current_menu = self.interface.get_menu_item_key()

        if current_menu == "RADIO_COM_1":

            strvalue = str(value).rjust(3, "0")
            newfreq = strvalue

            currentvalue =  int(self.interface.VALUES[f"RADIO_COM_1_STBY_{self.RADIO_ACTIVE_SEG}"])

            if currentvalue == 0 and value == 990:
                direction = 'DOWN'
                extra = 0
            elif value > int(self.interface.VALUES[f"RADIO_COM_1_STBY_{self.RADIO_ACTIVE_SEG}"]):
                direction = 'UP'
                extra = 5
            else:
                direction = 'DOWN'
                extra = -5


            if self.RADIO_ACTIVE_SEG == "RIGHT":

                strvalue = str(value).rjust(3, "0")
                newvalue = strvalue

                first = int(strvalue[:1])
                last = strvalue[-2:]

                if last in ["20", "45", "70", "95"]:

                    newlast = int(last) + extra

                    if newlast > 90:
                        newlast = 0
                        first += 1
                    if newlast < 0:
                        newlast = 90
                        first -= 1

                    if first > 9:
                        first = 0
                    if first < 0:
                        first = 9

                    newfreq = str(f'{first}{newlast}').ljust(3, "0")
                    encoder.encoder.writeCounter(int(newfreq))

            self.interface.VALUES[f"RADIO_COM_1_STBY_{self.RADIO_ACTIVE_SEG}"] = newfreq

            LEFT = self.interface.VALUES[f"RADIO_COM_1_STBY_LEFT"]
            RIGHT = self.interface.VALUES[f"RADIO_COM_1_STBY_RIGHT"]

            data = {
                "RADIO_COM_1_STBY": {
                    "ACTION": "ADJUST",
                    "FREQ": f"{LEFT}.{RIGHT}",
                    "DIRECTION": direction
                }
            }

            self.mqtt.client.publish("FS_DATA_IN", json.dumps(data))
            self.interface.standby.write(self.interface.standby.encode_string(f"{LEFT}.{RIGHT}"))

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

            new_stby = self.interface.VALUES['RADIO_COM_1_ACTIVE']

            self.interface.VALUES['RADIO_COM_1_ACTIVE'] = f"{self.interface.VALUES['RADIO_COM_1_STBY_LEFT']}.{self.interface.VALUES['RADIO_COM_1_STBY_RIGHT']}"

            bits = new_stby.split(".")

            self.interface.VALUES['RADIO_COM_1_STBY_LEFT'] = bits[0]
            self.interface.VALUES['RADIO_COM_1_STBY_RIGHT'] = bits[1]

            self.interface.update_radio_displays()

            data = {
                "RADIO_COM_1_STBY": {
                    "ACTION": "SWAP"
                }
            }
            self.mqtt.client.publish("FS_DATA_IN", json.dumps(data))

    def increment_value(self):
        pass
        # if self.interface.get_menu_item_key() == "RADIO_COM_1":
        #     self.send_radio_update("UP")
        

    def decrement_value(self):
        pass
        # if self.interface.get_menu_item_key() == "RADIO_COM_1":
        #     self.send_radio_update("DOWN")

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
            self.interface.radio_stby_flash()

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
                "color": 0x001100
            },
            "SPEED": {
                "step": 1,
                "min": 100,
                "max": 400,
                "color": 0x000011
            },
            "RADIO_COM_1_LEFT": {
                "step": 1,
                "min": 118,
                "max": 135,
                "color": 0x0f0f0f
            },
            "RADIO_COM_1_RIGHT": {
                "step": 5,
                "min": 0,
                "max": 990,
                "color": 0x110022
            }
        }

        key = self.interface.get_menu_item_key()

        if key == "RADIO_COM_1":
            key = f'{key}_{self.RADIO_ACTIVE_SEG}'

        return encoder_definitions[key]


    def run(self):
        print("starting")
        self.interface.clear()
        sleep(2)
        self.interface.update_radio_displays()
        while True:
            self.interface.show()


config = {
    'lcd_address': 0x27,
    'radio_displays': {
        'active': {
            'clk': 21,
            'dio': 20
        },
        'standby': {
            'clk': 26,
            'dio': 19
        }
    },
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
        'broker': "192.168.100.200",
        "client_name": "FMC_Desktop"
    }
}

fmc = FMC_Desktop(config)

fmc.interface.VALUES['RADIO_COM_1_ACTIVE'] = "122.800"
fmc.run()