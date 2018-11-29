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

MOTOR_LEFT = Motor(OUTPUT_A)
MOTOR_RIGHT = Motor(OUTPUT_B)
#motorBasket = Motor(OUTPUT_C)

LIGHT_LEFT = Sensor(INPUT_4)
COLOR_MIDDLE = Sensor(INPUT_3)
LIGHT_RIGHT = Sensor(INPUT_2)    
DISTANCE_FRONT = Sensor(INPUT_1)

LIGHT_LEFT.mode = LIGHT_RIGHT.mode = "REFLECT"
COLOR_MIDDLE.mode = "COL-AMBIENT"

COLOR_THRESHOLD = 20
LIGHT_THRESHOLD = 450

NORMAL_SPEED = 30

drive = MoveTank(MOTOR_LEFT, MOTOR_RIGHT)

def on_normal_speed():
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
    """
    returns correction_type
    """
    if not is_color_white(COLOR_MIDDLE):
        if (not is_light_white(LIGHT_LEFT)) and is_light_white(LIGHT_RIGHT):
            return "left"
        elif is_light_white(LIGHT_LEFT) and (not is_light_white(LIGHT_RIGHT)):
            return "right"
    return False


def correct_path():
    if line_correction_needed() == "left":
        drive.on(NORMAL_SPEED, int(NORMAL_SPEED / 2))
    elif line_correction_needed() == "right":
        drive.on(int(NORMAL_SPEED / 2), NORMAL_SPEED)
    if line_correction_needed():
        correct_path()
    return

while True:
    drive.on(NORMAL_SPEED, NORMAL_SPEED)
    correct_path()


