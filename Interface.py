#! /usr/bin/env python3

import i2c_lcd

class Interface():

    lcd = None
    lcd_address = None

    ACTIVE_MENU_ITEM = 0

    MENU_ITEMS = {
        "RADIO_COM_1": {
            "display_name": "Radio COM 1",
            "variable_left": "RADIO_COM_1_STBY_LEFT",
            "variable_right": "RADIO_COM_1_STBY_RIGHT",
            "variable_active": "RADIO_COM_1_ACTIVE"
        },
        "ALTITUDE": {
            "display_name": "Altitude",
            "variable": "ALTITUDE"
        },
        "HEADING": {
            "display_name": "Heading",
            "variable": "HEADING"
        },
        "SPEED": {
            "display_name": "Speed",
            "variable": "SPEED"
        }
    }

    VALUES = {
        'RADIO_COM_1_STBY_LEFT': 121,
        'RADIO_COM_1_STBY_RIGHT': 800,
        'RADIO_COM_1_ACTIVE': 0,
        'ALTITUDE': 0,
        'HEADING': 0,
        'SPEED': 0
    }

    def __init__(self, FMC, lcd_address):
        self.FMC = FMC
        self.lcd_address = lcd_address
        self.init_lcd()

    def init_lcd(self):
        self.lcd = i2c_lcd.lcd(addr=self.lcd_address)
        self.lcd.lcd_display_string_pos("FMC Desktop", 1, 0)
        self.lcd.lcd_display_string_pos("v0.0.2!", 2, 0)

    def get_menu_item_key(self):
        keys = list(self.MENU_ITEMS.keys())
        return keys[self.ACTIVE_MENU_ITEM]

    def get_menu_item_name(self):
        return self.MENU_ITEMS[self.get_menu_item_key()]['display_name']

    def show(self):
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

        if self.ACTIVE_MENU_ITEM == 0:
            content = self.get_radio_output()

        if self.ACTIVE_MENU_ITEM == 1:
            content = self.get_altitude_output()

        if self.ACTIVE_MENU_ITEM == 2:
            content = self.get_heading_output()

        if self.ACTIVE_MENU_ITEM == 3:
            content = self.get_speed_output()

        for row in content:
            rows.append(row)

        return rows

    def get_radio_output(self, raw=False):
        rows = []

        if self.VALUES['RADIO_COM_1_ACTIVE'] and self.VALUES['RADIO_COM_1_STBY_LEFT'] and self.VALUES['RADIO_COM_1_STBY_RIGHT']:
            standby = f"{str(self.VALUES['RADIO_COM_1_STBY_LEFT']).rjust(3, '0')}.{str(self.VALUES['RADIO_COM_1_STBY_RIGHT']).rjust(3, '0')}"
            active = self.VALUES['RADIO_COM_1_ACTIVE']

            output = f'{active}      {standby}'
            rows.append(output)

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

