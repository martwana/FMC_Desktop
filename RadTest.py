#! /usr/bin/env python3


import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time
import json
from SimConnect import *

class Server():

    def __init__(self):
        self.init_simconnect()

    def init_simconnect(self):
        self.sc = SimConnect()
        self.aircraftReqs = AircraftRequests(self.sc, _time=0)
        self.aircraftEvents = AircraftEvents(self.sc)
    
    def run(self):

        while False:

            values = [ 
                # "127.800", 
                # "127.805",
                # "127.810",
                # "127.815",
                # "127.820",
                # "127.825",
                # "127.830",
                # "127.835",
                # "127.840",
                # "127.845",
                # "127.850",
                # "127.855",
                # "127.860",
                # "127.865",
                "127.870",
                "127.875",
                "127.880",
                "127.885",
                "127.890",
                "127.895",

            ]

            def to_radio_bcd16(val):
              encodable = int(val * 100)
              remainder = ((val * 100) - encodable) / 100.0
              return int(str(encodable), 16), round(remainder,3), val

            for value in values:

                setterStr = 'COM_STBY_RADIO_SET'
                value = float(value)

                # print(value)

                encoded, remainder, value = to_radio_bcd16(value)

                # print(encoded, remainder, value)

                setter = self.aircraftEvents.find(setterStr)
                setter(encoded)

                # print( str(value).split('.')[1].ljust(3, "0"))

                last = str(value).split('.')[1].ljust(3, "0")[-2:]

                print(last)

                if last in ["05", "15", "35", "55", "65", "85", "95"]: 
                    self.aircraftEvents.find("COM_RADIO_FRACT_INC")()


                time.sleep(0.75)

                    # if last in ["20", "45", "70", "95"]:

            # if remainder == 0.005: # INCREMENT 3RD DECIMAL IF IT'S THERE (IGNORING THE ISSUE ABOVE)
            # #   # for _ in range(0, int(0.01 / remainder)):

            # elif remainder == 0.01:
            #     self.aircraftEvents.find("COM_RADIO_FRACT_INC")()
            #     self.aircraftEvents.find("COM_RADIO_FRACT_INC")()

            # time.sleep(1)




server = Server()
server.run()


