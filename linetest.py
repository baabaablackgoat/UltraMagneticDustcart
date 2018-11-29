#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor
from ev3dev2.sound import Sound
from ev3dev2 import fonts
import sys, os, math
def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

os.system('setfont ' + 'Lat15-Terminus12x6')

MOTOR_LEFT = OUTPUT_A
MOTOR_RIGHT = OUTPUT_B
#motorBasket = Motor(OUTPUT_C)

try:
    LIGHT_LEFT = Sensor(INPUT_2)
    COLOR_MIDDLE = Sensor(INPUT_3)
    LIGHT_RIGHT = Sensor(INPUT_4)    
    DISTANCE_FRONT = Sensor(INPUT_1)
except Exception as e:
    print('Sensor not found: ' + str(e))
    debug_print('Sensor not found' + str(e))
    

LIGHT_LEFT.mode = LIGHT_RIGHT.mode = "REFLECT"
COLOR_MIDDLE.mode = "COL-REFLECT"

COLOR_THRESHOLD = 20
LIGHT_THRESHOLD = 450

NORMAL_SPEED = 20

previous_action = False

try:
    drive = MoveTank(MOTOR_LEFT, MOTOR_RIGHT)
except Exception as e:
    print('Motor error: ' + str(e))
    debug_print('Motor error: ' + str(e))

def drive_normal_speed():
    drive.on(NORMAL_SPEED, NORMAL_SPEED)


def is_color_white(sensor):
    if sensor.value() >= COLOR_THRESHOLD:
        return True
    else:
        return False


def is_light_white(sensor):
    if sensor.value() >= LIGHT_THRESHOLD:
        return True
    else:
        return False


def line_correction_needed():
    global previous_action
    if not is_color_white(COLOR_MIDDLE): #? B ?
        if (not is_light_white(LIGHT_LEFT)) and is_light_white(LIGHT_RIGHT): #B B W
            previous_action = "left"
            return "left"
        elif is_light_white(LIGHT_LEFT) and (not is_light_white(LIGHT_RIGHT)): #W B B
            previous_action = "right"
            return "right"
        else: #W B W
            previous_action = False
            return False
    else: #color sensor is on white
        if previous_action == "left":
            return "offtrack-left"
        elif previous_action == "right":
            return "offtrack-right"
        else:
            return "event"


def correct_path(state):
    if state == "right":
        drive.on(NORMAL_SPEED , 0)
    elif state == "offtrack-right":
        drive.on(NORMAL_SPEED, math.floor(NORMAL_SPEED*-0.2))
    elif state == "left":
        drive.on(0, NORMAL_SPEED)
    elif state == "offtrack-left":
        drive.on(math.floor(NORMAL_SPEED*-0.2), NORMAL_SPEED)
    elif state == "event":
        drive.on(NORMAL_SPEED,NORMAL_SPEED)
    else:
        drive.on(NORMAL_SPEED,NORMAL_SPEED)


while True:
    state = line_correction_needed()
    print(state)
    correct_path(state)
