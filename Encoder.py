#! /usr/bin/env python3

import i2cEncoderLibV2
import time

class Encoder():

    def __init__(self, encoder_set, config):
        self.encoder_set = encoder_set

        self.config = config
        self.name = config['name']
        self.encoder = i2cEncoderLibV2.i2cEncoderLibV2(self.encoder_set.bus, config['address'])
        encconfig = (i2cEncoderLibV2.INT_DATA | i2cEncoderLibV2.WRAP_ENABLE | i2cEncoderLibV2.DIRE_RIGHT | i2cEncoderLibV2.IPUP_ENABLE | i2cEncoderLibV2.RMOD_X1 | i2cEncoderLibV2.RGB_ENCODER)
        self.encoder.begin(encconfig)
        
        init_config = self.encoder_set.get_encoder_definition(self.config['name'])
        
        self.set_encoder_config(init_config)
        self.set_event_handlers()

    def get_menu_items(self):
        return self.encoder_set.FMC.interface.MENU_ITEMS_KEYS

    def set_encoder_config(self, config):
        self.encoder.writeAntibouncingPeriod(50)
        self.encoder.writeDoublePushPeriod(50)
        self.encoder.writeStep(config['step'])
        self.encoder.writeMin(config['min'])
        self.encoder.writeMax(config['max'])
        self.encoder.writeRGBCode(config['color'])
        self.encoder.writeCounter(int(self.get_current_value(self.config['name'])))

    def set_event_handlers(self):
        self.encoder.onChange = self.on_encoder_change
        self.encoder.onButtonPush = self.on_encoder_push
        self.encoder.onButtonDoublePush = self.on_encoder_double_push
        self.encoder.onIncrement = self.on_encoder_increment
        self.encoder.onDecrement = self.on_encoder_decrement

        self.encoder.autoconfigInterrupt()

    def on_encoder_push(self, encoder):
        if self.config['name'] == "menu":
            pass
        else:
            self.encoder_set.FMC.button_press()

    def on_encoder_increment(self, encoder):
        if self.config['name'] == "menu":
            pass
        else:
            self.encoder_set.FMC.increment_value()

    def on_encoder_decrement(self, encoder):
        if self.config['name'] == "menu":
            pass
        else:
            self.encoder_set.FMC.decrement_value()

    def on_encoder_double_push(self, encoder):
        if self.config['name'] == "menu":
            pass
        else:
            self.encoder_set.FMC.double_button_press()

    def on_encoder_change(self, encoder):
        value = encoder.readCounter32()

        if self.config['name'] == "menu":
            self.encoder_set.FMC.interface.ACTIVE_MENU_ITEM = value
            self.encoder_set.encoders['value'].set_encoder_config(self.encoder_set.FMC.get_encoder_definition())
        else:
            self.encoder_set.FMC.update_value(self, value)

    def update_status(self):
        self.encoder.updateStatus()

    def get_current_value(self, name):
        if name == "menu":
            return self.encoder_set.FMC.interface.ACTIVE_MENU_ITEM
        elif name == "value":
            return self.encoder_set.FMC.get_current_value()