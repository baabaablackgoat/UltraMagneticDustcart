#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor
from ev3dev2.sound import Sound
import sys
def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

motorLeft = Motor(OUTPUT_A)
motorRight = Motor(OUTPUT_B)
#motorBasket = Motor(OUTPUT_C)

lightLeft = Sensor(INPUT_4)
colorMiddle = Sensor(INPUT_3)
lightRight = Sensor(INPUT_2)    
distanceFront = Sensor(INPUT_1)

lightLeft.mode = lightRight.mode = "REFLECT"
colorMiddle.mode = "COL-AMBIENT"

"""
    color sensor: white > 20
    light sensor: white > 450
"""
soundEmitter = Sound()
#soundEmitter.play_file("victory.wav", 100)

while True:
    if lightLeft.value() < 450:
        pass
    if lightRight.value() < 450:
        pass
    
    #special events
    if colorMiddle.value() < 20:
        pass
    #if not motorLeft.is_running:
    #    motorLeft.on(20)
    #motorLeft.stop()



