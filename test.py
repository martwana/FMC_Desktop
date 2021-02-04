#! /usr/bin/env python3

import i2c_lcd
import smbus2
import RPi.GPIO as GPIO
import time
import i2cEncoderLibV2

class RadioStack():

    FREQ_SEG_1 = 121
    FREQ_SEG_2 = 500
    FREQ_SEC_ACTIVE = 2

    ALTITUDE = 0
    ALTITUDE_STEP = 100

    HEADING = 0
    ACTIVE_HEADING = 0

    SPEED = 0
    ACTIVE_SPEED = 0

    config = {}
    bus = None

    encoders = {}

    status = False

    ACTIVE_FREQ_SEG_1 = 121
    ACTIVE_FREQ_SEG_2 = 500

    ACTIVE_ALTITUDE = 0

    LAST_RECEIVED_ADDR = 0

    encoder_int_pin = 4

    ACTIVE_MENU_ITEM = 1

    MENU_ITEMS_KEYS = [
        "radio_com_1",
        "altitude",
        "heading",
        "speed"
    ]

    MENU_ITEMS = {
        "radio_com_1": {
            "display_name": "Radio COM 1"
        },
        "altitude": {
            "display_name": "Altitude"
        },
        "heading": {
            "display_name": "Heading"
        },
        "speed": {
            "display_name": "Speed"
        }
    }

    def __init__(self, config):
        self.config = config

        self.bus = smbus2.SMBus(1)

        GPIO.setmode(GPIO.BCM)

        self.init_lcd()
        self.init_encoders()

        self.last_active = time.time()


    def init_encoders(self):
        GPIO.setup(self.encoder_int_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for encoderName in self.config['encoders'].keys():
            encoder = self.config['encoders'][encoderName]

            name = encoder['name']
            encoderAddress = encoder['address']

            self.encoders[encoderAddress] = i2cEncoderLibV2.i2cEncoderLibV2(self.bus, encoderAddress)

            encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
            self.encoders[encoderAddress].begin(encconfig)

            self.init_encoder_value(encoderAddress, name)

            self.flash_encoder(encoderAddress)
        
            self.encoders[encoderAddress].writeRGBCode(0x110011)

        GPIO.add_event_detect(self.encoder_int_pin, GPIO.FALLING, callback=self.encoderInt, bouncetime=10)

    def encoderInt(self, pin):
        for encoder in self.encoders.keys():
            self.encoders[encoder].updateStatus()


    def flash_encoder(self, encoderAddress):
        self.encoders[encoderAddress].writeRGBCode(0x640000)
        time.sleep(0.2)
        self.encoders[encoderAddress].writeRGBCode(0x006400)
        time.sleep(0.2)
        self.encoders[encoderAddress].writeRGBCode(0x000064)
        time.sleep(0.2)

    def init_altitude_encoder(self, encoderAddress):
        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

        self.encoders[encoderAddress].writeCounter(self.ALTITUDE)
        self.encoders[encoderAddress].writeStep(self.ALTITUDE_STEP)
        self.encoders[encoderAddress].writeMin(0)
        self.encoders[encoderAddress].writeMax(50000)

        def AltEncoderChange(encoder):
            self.last_active = time.time()
            value = self.encoders[encoderAddress].readCounter32()

            self.LAST_RECEIVED_ADDR = encoder.i2cadd
            self.ALTITUDE = value
            
        def AltEncoderDoublePush(encoder):
            self.ACTIVE_ALTITUDE = self.ALTITUDE

        def AltEncoderPush(encoder):
            if self.ALTITUDE_STEP == 100:
                self.ALTITUDE_STEP = 1000
            else:
                self.ALTITUDE_STEP = 100

            self.encoders[encoderAddress].writeStep(self.ALTITUDE_STEP)

        self.encoders[encoderAddress].onChange = AltEncoderChange
        self.encoders[encoderAddress].onButtonPush = AltEncoderPush
        self.encoders[encoderAddress].onButtonDoublePush = AltEncoderDoublePush
        self.encoders[encoderAddress].autoconfigInterrupt()

    def init_heading_encoder(self, encoderAddress):
        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

        self.encoders[encoderAddress].writeCounter(self.HEADING)
        self.encoders[encoderAddress].writeStep(1)
        self.encoders[encoderAddress].writeMin(0)
        self.encoders[encoderAddress].writeMax(359)

        def HdgEncoderChange(encoder):
            self.last_active = time.time()
            value = self.encoders[encoderAddress].readCounter32()

            self.LAST_RECEIVED_ADDR = encoder.i2cadd
            self.HEADING = value
            
        def HdgEncoderPush(encoder):
            self.ACTIVE_HEADING = self.HEADING

        self.encoders[encoderAddress].onChange = HdgEncoderChange
        self.encoders[encoderAddress].onButtonPush = HdgEncoderPush
        self.encoders[encoderAddress].autoconfigInterrupt()

    def init_speed_encoder(self, encoderAddress):
        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

        self.encoders[encoderAddress].writeCounter(self.SPEED)
        self.encoders[encoderAddress].writeStep(1)
        self.encoders[encoderAddress].writeMin(0)
        self.encoders[encoderAddress].writeMax(450)

        def SpdEncoderChange(encoder):
            self.last_active = time.time()
            value = self.encoders[encoderAddress].readCounter32()

            self.LAST_RECEIVED_ADDR = encoder.i2cadd
            self.SPEED = value
            
        def SpdEncoderPush(encoder):
            self.ACTIVE_SPEED = self.SPEED

        self.encoders[encoderAddress].onChange = SpdEncoderChange
        self.encoders[encoderAddress].onButtonPush = SpdEncoderPush
        self.encoders[encoderAddress].autoconfigInterrupt()

    def init_radio_encoder(self, encoderAddress):

        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

        self.freq_seg_2_config(encoderAddress)

        def FreqEncoderChange(encoder):
            self.last_active = time.time()
            value = self.encoders[encoderAddress].readCounter32()

            self.LAST_RECEIVED_ADDR = encoder.i2cadd

            if self.FREQ_SEC_ACTIVE == 1:
                self.FREQ_SEG_1 = value
            else:
                self.FREQ_SEG_2 = value

        def FreqEncoderPush(encoder):
            if self.FREQ_SEC_ACTIVE == 1:
                self.FREQ_SEC_ACTIVE = 2
                self.freq_seg_2_config(encoderAddress)
            else: 
                self.FREQ_SEC_ACTIVE = 1
                self.freq_seg_1_config(encoderAddress)

        def FreqEncoderDoublePush(encoder):
            self.activate_frequency()

        self.encoders[encoderAddress].onChange = FreqEncoderChange
        self.encoders[encoderAddress].onButtonPush = FreqEncoderPush
        self.encoders[encoderAddress].onButtonDoublePush = FreqEncoderDoublePush
        self.encoders[encoderAddress].autoconfigInterrupt()

    def freq_seg_1_config(self, encoderAddress):
        self.encoders[encoderAddress].writeCounter(self.FREQ_SEG_1)
        self.encoders[encoderAddress].writeStep(1)
        self.encoders[encoderAddress].writeMin(118)
        self.encoders[encoderAddress].writeMax(137)
        

    def freq_seg_2_config(self, encoderAddress):
        self.encoders[encoderAddress].writeCounter(self.FREQ_SEG_2)
        self.encoders[encoderAddress].writeStep(25)
        self.encoders[encoderAddress].writeMin(0)
        self.encoders[encoderAddress].writeMax(975)

    def activate_frequency(self):
        self.ACTIVE_FREQ_SEG_1 = self.FREQ_SEG_1
        self.ACTIVE_FREQ_SEG_2 = self.FREQ_SEG_2

    def init_value_encoder(self, encoderAddress):
        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

    def init_encoder_value(self, encoderAddress, name):

        if name == "freq":
            self.encoders[encoderAddress].writeCounter(self.FREQ_SEG_2)
            self.init_radio_encoder(encoderAddress)

        if name == "control":
            self.encoders[encoderAddress].writeCounter(0)
            self.init_value_encoder(encoderAddress)

        if name == "menu":
            self.encoders[encoderAddress].writeCounter(1)
            self.init_menu_encoder(encoderAddress, name)

    def init_menu_encoder(self, encoderAddress, name):

        self.encoders[encoderAddress].writeAntibouncingPeriod(10)
        self.encoders[encoderAddress].writeDoublePushPeriod(50)

        self.encoders[encoderAddress].writeStep(1)
        self.encoders[encoderAddress].writeMin(0)
        self.encoders[encoderAddress].writeMax(len(self.MENU_ITEMS_KEYS) - 1)


        def MenuEncoderChange(encoder):
            self.last_active = time.time()
            value = self.encoders[encoderAddress].readCounter32()

            self.LAST_RECEIVED_ADDR = encoder.i2cadd
            self.ACTIVE_MENU_ITEM = value

            config_name = self.MENU_ITEMS_KEYS[value]

            self.set_encoder_steps(config_name)

        self.encoders[encoderAddress].onChange = MenuEncoderChange

        self.encoders[encoderAddress].autoconfigInterrupt()

    def set_encoder_steps(self, config_name):

        if config_name == "radio_com_1":
            self.init_radio_encoder(self.config['encoders']['value']['address'])

        if config_name == "altitude":
            self.init_altitude_encoder(self.config['encoders']['value']['address'])

        if config_name == "heading":
            self.init_heading_encoder(self.config['encoders']['value']['address'])

        if config_name == "speed":
            self.init_speed_encoder(self.config['encoders']['value']['address'])


    def init_lcd(self):
        self.lcd = i2c_lcd.lcd(addr=self.config['lcd_address'])
        self.print_start_message()

    def print_start_message(self):
        self.lcd.lcd_display_string_pos("FMC Desktop", 1, 0)
        self.lcd.lcd_display_string_pos("v0.0.1!", 2, 0)

    def isRadioSet(self):
        if self.FREQ_SEG_1 != self.ACTIVE_FREQ_SEG_1 or self.FREQ_SEG_2 != self.ACTIVE_FREQ_SEG_2:
            return False
        return True

    def isAltitudeSet(self):
        if self.ALTITUDE != self.ACTIVE_ALTITUDE:
            return False
        return True

    def isHeadingSet(self):
        if self.HEADING != self.ACTIVE_HEADING:
            return False
        return True

    def isSpeedSet(self):
        if self.SPEED != self.ACTIVE_SPEED:
            return False
        return True

    def get_radio_output(self, raw=False):
        rows = []
        if self.isRadioSet():
            status = "Set    "
        else:
            status = "Not set"

        output = f'{self.FREQ_SEG_1}.{str(self.FREQ_SEG_2).rjust(3, "0")} - {status}'

        if raw:
            return output

        rows.append(output)

        if self.FREQ_SEC_ACTIVE == 1:
            rows.append(" ^")
        else: 
            rows.append("     ^")

        return rows


    def get_altitude_output(self, raw=False):
        rows = []
        if self.isAltitudeSet():
            status = "Set    "
        else:
            status = "Not set"

        output = f'{str(self.ALTITUDE).rjust(5, "0")} ft - {status}'

        if raw:
            return output

        rows.append(output)

        return rows


    def get_heading_output(self, raw=False):
        rows = []
        if self.isHeadingSet():
            status = "Set    "
        else:
            status = "Not set"

        output = f'{str(self.HEADING).rjust(3, "0")}* - {status}'

        if raw:
            return output

        rows.append(output)

        return rows

    def get_speed_output(self, raw=False):
        rows = []
        if self.isSpeedSet():
            status = "Set    "
        else:
            status = "Not set"

        output = f'{str(self.SPEED).rjust(3, "0")} kts - {status}'

        if raw:
            return output

        rows.append(output)

        return rows

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


    def run(self):
        self.lcd.lcd_clear()

        self.last_active = time.time() - 10

        while True:

            if (time.time() - self.last_active) < 10:
                rows = []
                rows.append("Actv: %s" % self.MENU_ITEMS[self.MENU_ITEMS_KEYS[self.ACTIVE_MENU_ITEM]]['display_name'])
                rows = self.append_content(rows)
                rows += [''] * (4 - len(rows))

            else:
                rows = []
                rows.append(self.get_radio_output(raw=True))
                rows.append(self.get_altitude_output(raw=True))
                rows.append(self.get_heading_output(raw=True))
                rows.append(self.get_speed_output(raw=True))

            for i in range(len(rows)):
                self.lcd.lcd_display_string_pos(rows[i].ljust(20, " "), (i + 1), 0)



config = {
    'lcd_address': 0x27,
    'encoders': {
        "value": {
            'name': "value",
            'address': 0x40,
            'int_pin': 1
        },
        "menu": {
            'name': "menu",
            'address': 0x50,
            'int_pin': 2
        }
    }
}

radioStack = RadioStack(config)

radioStack.run()



    


    
    
