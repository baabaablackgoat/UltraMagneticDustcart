#!/usr/bin/env python3
#from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor
#import time
import threading, sys
#xd = MoveTank(OUTPUT_A, OUTPUT_B)
#xd.on_for_degrees(10, 20, 90)
#time.sleep(5)
#xd.on_for_rotations(20, 20, 2)

"""motor max speed ist immer 100


"""
#motor_c = Motor(OUTPUT_C)
#motor_c.on_for_seconds(100,2)

def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

LightSensorLeft = Sensor(INPUT_4)
LightSensorMiddle = Sensor(INPUT_3)
LightSensorRight = Sensor(INPUT_2)
LightSensorLeft.mode = 'REFLECT'
LightSensorMiddle.mode = 'COL-AMBIENT'
LightSensorRight.mode = 'REFLECT'

'''
    Bei REFLECT bzw Farbsensor auf COL-AMBIENT sind lichter an.
    Middle bei Schwarz 10, weiß 30-40
    Left/Right bei Schwarz 350, 600. AUCH IM TUNNEL BEI REFLECT
'''

def logdataInterval():
    def logdata():
        logdataInterval()
        debug_print("Left: ", LightSensorLeft.value())
        debug_print("Middle: ", LightSensorMiddle.value() * 10)
        debug_print("Right: ", LightSensorRight.value())
    t = threading.Timer(0.1, logdata)
    t.start()
    return t

logdataInterval()