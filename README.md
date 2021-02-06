This is a little DIY FMC controller for SimConnect. My main motivation for this is that when flying on VATSIM, it takes me a while to change the radio frequency in the aircraft with a mouse. In FS2020, the motion effects can cause you zoom unintentionally, so I wanted something physical to use to change it.

Current State: Working

Start server once Sim is running, followed by pi app. It will begin reading data from the Sim to populate the state. 
Latency seems to be extremely low. 

For SPD, ALT and HDG, I am able to set the values directly using Events. 

For Radio, it was more complicated due to frequency steps. So, every time you turn the knob on the box, it triggers an increment event on the side(left-right/MHz-Hz) of the frequency you are changing. The server transmits the new value back to the Pi instantly to update the display. 


The hardware required for this is:

1 x Raspberry Pi
1 x 20x4 LCD with an I2C backpack
2 x RGB Rotary Encoders 
2 x Rotary Encoder I2C chips
1 x Logic Level Converter

FMC_Desktop.py runs on the Raspberry Pi
FMC_Desktop_Server.py runs on the machine

TODO:
[] - make better use of the screen real-estate - get all data on a single screen
[] - Generate a board wiring diagram
[] - Get it off the breadboard
[] - Get it in an enclosure

/u/martwana 
