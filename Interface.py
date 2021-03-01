#! /usr/bin/env python3

import i2c_lcd
import TM1637
from time import sleep

class Interface():

    lcd = None
    config = None

    ACTIVE_MENU_ITEM = 0

    MENU_ITEMS = {
        "RADIO_COM_1": {
            "display_name": "Radio COM 1",
            "variable_left": "RADIO_COM_1_STBY_LEFT",
            "variable_right": "RADIO_COM_1_STBY_RIGHT",
            "variable_active": "RADIO_COM_1_ACTIVE"
        },
        "SPEED": {
            "display_name": "Speed",
            "variable": "SPEED"
        },
        "HEADING": {
            "display_name": "Heading",
            "variable": "HEADING"
        },
        "ALTITUDE": {
            "display_name": "Altitude",
            "variable": "ALTITUDE"
        }
        
    }

    VALUES = {
        'RADIO_COM_1_STBY_LEFT': 121,
        'RADIO_COM_1_STBY_RIGHT': 500,
        'RADIO_COM_1_ACTIVE': 0,
        'ALTITUDE': 0,
        'HEADING': 0,
        'SPEED': 100
    }

    def __init__(self, FMC, config):
        self.FMC = FMC
        self.init_lcd()
        self.init_radio_displays()

    def init_lcd(self):
        self.lcd = i2c_lcd.lcd(addr=self.FMC.config['lcd_address'])
        self.lcd.lcd_display_string_pos("FMC Desktop", 1, 0)
        self.lcd.lcd_display_string_pos("v0.0.2!", 2, 0)

    def init_radio_displays(self):
        active_config = self.FMC.config['radio_displays']['active']
        standby_config = self.FMC.config['radio_displays']['standby']

        self.active = TM1637.TM1637Decimal(clk=active_config['clk'], dio=active_config['dio'])
        self.standby = TM1637.TM1637Decimal(clk=standby_config['clk'], dio=standby_config['dio'])

        self.active.brightness(0)
        self.standby.brightness(0)

        self.active.write([0, 0, 0, 0, 0, 0])
        self.standby.write([0, 0, 0, 0, 0, 0])

    def update_radio_displays(self):
        self.active.write(self.active.encode_string(self.VALUES['RADIO_COM_1_ACTIVE']))
        self.standby.write(self.standby.encode_string(f"{self.VALUES['RADIO_COM_1_STBY_LEFT']}.{self.VALUES['RADIO_COM_1_STBY_RIGHT']}"))

    def dim_radios(self):
        self.active.brightness(0)
        self.standby.brightness(0)

    def light_radios(self):
        self.active.brightness(2)
        self.standby.brightness(2)

    def radio_stby_flash(self):
        self.standby.write([0, 0, 0, 0, 0, 0])
        sleep(0.08)
        self.standby.write(self.standby.encode_string(f"{self.VALUES['RADIO_COM_1_STBY_LEFT']}.{self.VALUES['RADIO_COM_1_STBY_RIGHT']}"))
        sleep(0.08)
        self.standby.write([0, 0, 0, 0, 0, 0])
        sleep(0.08)
        self.standby.write(self.standby.encode_string(f"{self.VALUES['RADIO_COM_1_STBY_LEFT']}.{self.VALUES['RADIO_COM_1_STBY_RIGHT']}"))


    def get_menu_item_key(self):
        keys = list(self.MENU_ITEMS.keys())
        return keys[self.ACTIVE_MENU_ITEM]

    def get_menu_item_name(self):
        return self.MENU_ITEMS[self.get_menu_item_key()]['display_name']

    def show(self):

        self.active.write(self.active.encode_string(self.VALUES['RADIO_COM_1_ACTIVE']))

        rows = []
        rows.append(f"{self.get_menu_item_name()}")
        rows = self.append_content(rows)
        rows += [''] * (4 - len(rows))

        for i in range(len(rows)):
            self.lcd.lcd_display_string_pos(rows[i].ljust(20, " "), (i + 1), 0)

    def clear(self):
        self.lcd.lcd_clear()

    def get_encoder_definition(self):
        return {
                "step": 1,
                "min": 0,
                "max": len(self.MENU_ITEMS) - 1,
                "color": 0xFF0000
            }

    def append_content(self, rows):

        content = []

        # self.dim_radios()

        if self.ACTIVE_MENU_ITEM == 0:
            # self.light_radios()
            content = self.get_radio_output()

        if self.ACTIVE_MENU_ITEM == 1:
            content = self.get_speed_output()

        if self.ACTIVE_MENU_ITEM == 2:
            content = self.get_heading_output()

        if self.ACTIVE_MENU_ITEM == 3:
            content = self.get_altitude_output()

        for row in content:
            rows.append(row)

        return rows

    def get_radio_output(self, raw=False):
        rows = []

        # if self.VALUES['RADIO_COM_1_ACTIVE'] and self.VALUES['RADIO_COM_1_STBY_LEFT'] and self.VALUES['RADIO_COM_1_STBY_RIGHT']:
        #     standby = f"{str(self.VALUES['RADIO_COM_1_STBY_LEFT']).rjust(3, '0')}.{str(self.VALUES['RADIO_COM_1_STBY_RIGHT']).rjust(3, '0')}"
        #     active = self.VALUES['RADIO_COM_1_ACTIVE']

        #     output = f'{active}      {standby}'
        #     rows.append(output)

        return rows

    def get_altitude_output(self, raw=False):
        rows = []
        output = f"{str(self.VALUES['ALTITUDE']).rjust(5, '0')} ft"
        rows.append(output)
        return rows

    def get_heading_output(self, raw=False):
        rows = []
        output = f"{str(self.VALUES['HEADING']).rjust(3, '0')}*"
        rows.append(output)
        return rows

    def get_speed_output(self, raw=False):
        rows = []
        output = f"{str(self.VALUES['SPEED']).rjust(3, '0')} kts"
        rows.append(output)
        return rows

