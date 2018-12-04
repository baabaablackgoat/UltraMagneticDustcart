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

soundemitter = Sound()

try:
    LIGHT_LEFT = Sensor(INPUT_4)
    COLOR_MIDDLE = Sensor(INPUT_3)
    LIGHT_RIGHT = Sensor(INPUT_2)    
    DISTANCE_FRONT = Sensor(INPUT_1)
except Exception as e:
    print('Sensor not found: ' + str(e))
    debug_print('Sensor not found' + str(e))
    

LIGHT_LEFT.mode = LIGHT_RIGHT.mode = "REFLECT"
COLOR_MIDDLE.mode = "COL-REFLECT"

COLOR_THRESHOLD = 170
LIGHT_THRESHOLD = 350

NORMAL_SPEED = 30

program_position = 0
# 0 before uturn, 1 before roadblock, 2 before pushing the block, 3 before dropoff
previous_action = False

try:
    drive = MoveTank(MOTOR_LEFT, MOTOR_RIGHT)
except Exception as e:
    print('Motor error: ' + str(e))
    debug_print('Motor error: ' + str(e))

def drive_normal_speed():
    drive.on(NORMAL_SPEED, NORMAL_SPEED)


def is_color_white(sensor):
    return sensor.value() * 10 >= COLOR_THRESHOLD


def is_light_white(sensor):
    return sensor.value() >= LIGHT_THRESHOLD


def line_correction_needed():
    global previous_action
    if (not is_light_white(LIGHT_LEFT)) and is_light_white(LIGHT_RIGHT): #B x W
        previous_action = "left"
        return "left"
    elif is_light_white(LIGHT_LEFT) and (not is_light_white(LIGHT_RIGHT)): #W x B
        previous_action = "right"
        return "right"
    elif is_color_white(COLOR_MIDDLE) and is_light_white(LIGHT_LEFT) and is_light_white(LIGHT_RIGHT): #W W W
        if previous_action == "left":
            return "offtrack-left"
        elif previous_action == "right":
            return "offtrack-right"
    else:
        previous_action = None
        return False


def correct_path(state):
    if state == "right":
        drive.on(NORMAL_SPEED , 0)
        #soundemitter.tone([(300, 300, 100)])
    elif state == "offtrack-right":
        drive.on(NORMAL_SPEED, math.floor(NORMAL_SPEED*-0.2))
        #soundemitter.tone([(300, 50, 100),(300, 50, 100)])
    elif state == "left":
        drive.on(0, NORMAL_SPEED)
        #soundemitter.tone([(450, 300, 100)])
    elif state == "offtrack-left":
        drive.on(math.floor(NORMAL_SPEED*-0.2), NORMAL_SPEED)
        #soundemitter.tone([(450, 50, 100),(450, 50, 100)])
    elif state == "event":
        drive.on(NORMAL_SPEED,NORMAL_SPEED)
    else:
        drive.on(NORMAL_SPEED,NORMAL_SPEED)



def u_turn():
    drive.on_for_degrees(NORMAL_SPEED, NORMAL_SPEED * -1, 180)

def push_block():
    pass

def wait_on_roadblock():
    pass

def ball_dropoff():
    pass


while True:
    state = line_correction_needed()
    print(state)
    correct_path(state)
