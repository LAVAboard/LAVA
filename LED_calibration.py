#! /usr/bin/env python

from gpiozero import OutputDevice
from time import sleep
import numpy as np
import sys

din = OutputDevice(10) #mosi, pin 19
clk = OutputDevice(11) #sclk, pin 23
lat = OutputDevice(8) #ce0, pin 24
_oe = OutputDevice(17) #GPIO17, pin 11

#initialize array of PWM values for the 24 channels
pwmbuffer = np.zeros(24, dtype = np.uint16)

#define function for setting PWM (update value in pwmbuffer)
def setPWM(chan, pwm):
        if pwm >  4095:
                sys.exit("error: pwm must be  0 - 4095")
        if chan > 23:
                sys.exit("error: channel must be 0 - 23") 
        pwmbuffer[chan] = pwm
        return

#define write function (encode PWM values to TLC5947 over SPI)
def writePWM():
        lat.off()
        #24 channels
        for c in range(23, -1, -1):
                #12 bits per channel, MSB first
                for b in range(11,-1, -1):
                        clk.off()
                        #if bit has a value, send pulse to TLC
                        if pwmbuffer[c] & (0b1<<b): 
                                din.on()
                        else:
                                din.off()
                        clk.on()

        clk.off()
        lat.on()
        lat.off()
        return

#power meter measurements: set known PWM, measure light intensity in uW/mm^2
for well in range(0, 24):
        setPWM(well, 4095)
        writePWM()
        print("align")
        sleep(20) #allow 20 seconds to align power meter
        print("get ready")
        sleep(3)
        for i in range(0, 22):
                PWMvalues = [4095, 4000, 3800, 3600, 3400, 3200, 3000, 2800, 2600, 2400, 2200, 2000, 1800, 1600, 1400, 1200, 1000, 800, 600, 400, 200, 0]
                setPWM(well, PWMvalues[i])
                writePWM()
                print(well)
                print(i)
                print(pwmbuffer)
                sleep(4) #allow 4 second between intensity changes to record light intensity
        print("done")
        sleep(2)
