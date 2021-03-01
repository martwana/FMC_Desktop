#! /usr/bin/env python3

import RPi.GPIO as GPIO
import smbus2
import Encoder

class EncoderSet():

    encoders = {}

    def __init__(self, FMC, config):
        self.FMC = FMC
        self.config = config
        self.bus = smbus2.SMBus(1)

        self.init_interrupt_pin()
        self.init_encoders()
        self.add_gpio_event_detect()

    def init_interrupt_pin(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.config['interrupt_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def add_gpio_event_detect(self):
        GPIO.add_event_detect(self.config['interrupt_pin'], GPIO.FALLING, callback=self.encoder_interrupt, bouncetime=5)

    def encoder_interrupt(self, pin):
        for encoder in self.encoders.keys():
            self.encoders[encoder].update_status()

    def init_encoders(self):
        for encoder in self.config['device_mapping']:
            enc = Encoder.Encoder(self, encoder)
            self.encoders[encoder['name']] = enc

    def get_encoder_definition(self, mode):
        if mode == "value":
            return self.FMC.get_encoder_definition()
        elif mode == "menu":
            return self.FMC.interface.get_encoder_definition()

        return False