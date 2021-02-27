#! /usr/bin/env python3

import TM1637
from time import sleep

active = TM1637.TM1637Decimal(clk=21, dio=20)
standby = TM1637.TM1637Decimal(clk=26, dio=19)

active.brightness(0)
standby.brightness(0)

active.write([0, 0, 0, 0, 0, 0])
standby.write([0, 0, 0, 0, 0, 0])



# def encode_string(string):
#     split = string.split('.')
#     parts = [ i[::-1] for i in split  ]
#     newString = '.'.join(parts)

#     print(newString)

#     return tm.encode_string(newString)

khz_range = [
    {
        "display": 5,
        "freq": 0
    },
    {
        "display": 10,
        "freq": 83
    },
    {
        "display": 15,
        "freq": 166
    },
    {
        "display": 30,
        "freq": 250
    },
    {
        "display": 35,
        "freq": 333
    },
    {
        "display": 40,
        "freq": 416
    },
    {
        "display": 55,
        "freq": 500
    },
    {
        "display": 60,
        "freq": 583
    },
    {
        "display": 65,
        "freq": 666
    },
    {
        "display": 80,
        "freq": 750
    },
    {
        "display": 85,
        "freq": 833
    },
    {
        "display": 90,
        "freq": 916
    }
]


for mhz in range(118, 136):
    khz = 0

    while khz < 1000:

        khz_str = str(khz)

        last = str(khz).rjust(3, "0")[-2:]
        khz += 5

        if last == "20" or last == "45" or last == "70" or last == "95":
            continue

        active.write(active.encode_string(f"{mhz}.{khz_str.rjust(3, '0')}"))
        standby.write(standby.encode_string(f"{mhz}.{khz_str.rjust(3, '0')}"))

        sleep(0.001)




# tm.numbers(12, 59)


# for i in range(100, 200):
#     tm.write([i, i, i, i, i, i])

#     sleep(0.1)

# all LEDS on "88:88"
# tm.write([127, 127, 227, 127, 127, 127])

# all LEDS off
# tm.write([0, 0, 0, 0])

# # show "0123"
# tm.write([63, 6, 91, 79])

# # show "COOL"
# tm.write([0b00111001, 0b00111111, 0b00111111, 0b00111000])

# # show "HELP"
# tm.show('123.45')

# # display "dEAd", "bEEF"
# tm.hex(0xdead)
# tm.hex(0xbeef)

# # show "12:59"
# tm.numbers(12, 59)

# # show "-123"
# tm.number(-123)

# # show temperature '24*C'
# tm.temperature(24)