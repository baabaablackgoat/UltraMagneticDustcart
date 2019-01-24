#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4, Sensor
from ev3dev2.sound import Sound
from ev3dev2 import fonts
import sys, os, math, time
def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

os.system('setfont ' + 'Lat15-Terminus12x6')

MOTOR_LEFT = OUTPUT_A
MOTOR_RIGHT = OUTPUT_B
MOTOR_BASKET = Motor(OUTPUT_C)

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
DISTANCE_FRONT.mode = "US-DIST-CM"

COLOR_THRESHOLD = 400 # 450 - 350
LIGHT_THRESHOLD = 350 # 400 - 170

NORMAL_SPEED = 35

program_position = 5

previous_action = False

last_three_white_passages = [30, 20, 10]
recently_added = False
roadblock_detected = False
ball_dropoff_detected = False
block_pushed = False
back_on_track_reached = False

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

def get_distance():
    return DISTANCE_FRONT.value() / 10

def add_new_white_passage():
    last_three_white_passages[2] = last_three_white_passages[1]
    last_three_white_passages[1] = last_three_white_passages[0]
    last_three_white_passages[0] = time.time()
    soundemitter.tone(1500, 50, play_type="PLAY_NO_WAIT_FOR_COMPLETE")

def line_correction_needed():
    global previous_action
    if (not is_light_white(LIGHT_LEFT)) and is_light_white(LIGHT_RIGHT): #B x W
        previous_action = "left"
        return "left"
    elif is_light_white(LIGHT_LEFT) and (not is_light_white(LIGHT_RIGHT)): #W x B
        previous_action = "right"
        return "right"
    elif is_color_white(COLOR_MIDDLE) and is_light_white(LIGHT_LEFT) and is_light_white(LIGHT_RIGHT): #W W W
        check_and_drive_first_uturn()
        if previous_action == "left":
            return "offtrack-left"
        elif previous_action == "right":
            return "offtrack-right"
    else:
        previous_action = None
        return False


def correct_path(state):
    if state == "right":
        drive.on(NORMAL_SPEED , -5)
        #soundemitter.tone([(300, 300, 100)])
    elif state == "offtrack-right":
        drive.on(NORMAL_SPEED, math.floor(NORMAL_SPEED*-0.25))
        #soundemitter.tone([(300, 50, 100),(300, 50, 100)])
    elif state == "left":
        drive.on(-5, NORMAL_SPEED)
        #soundemitter.tone([(450, 300, 100)])
    elif state == "offtrack-left":
        drive.on(math.floor(NORMAL_SPEED*-0.25), NORMAL_SPEED)
        #soundemitter.tone([(450, 50, 100),(450, 50, 100)])
    elif state == "event":
        drive.on(NORMAL_SPEED,NORMAL_SPEED)
    else:
        drive.on(NORMAL_SPEED,NORMAL_SPEED)


def check_and_drive_first_uturn():
    global program_position
    if program_position == 0:
        drive.on_for_seconds(NORMAL_SPEED, NORMAL_SPEED, 0.25)
        drive.on_for_rotations(left_speed=-50, right_speed=50, rotations=1)
        drive.on(NORMAL_SPEED, NORMAL_SPEED)
        while(is_color_white(COLOR_MIDDLE) and is_light_white(LIGHT_LEFT) and is_light_white(LIGHT_RIGHT)):
            pass
        program_position = 1
        soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")


# After doing the first u-turn, detect obstacles in short distance
def wait_on_roadblock():
    global program_position, roadblock_detected, NORMAL_SPEED
    if program_position == 1:
        while(get_distance() < 8):
            roadblock_detected = True
            drive.off()
        if roadblock_detected:
            NORMAL_SPEED = math.floor(NORMAL_SPEED * 0.8)
            drive.on(NORMAL_SPEED, NORMAL_SPEED)
            program_position = 2
            soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")


# After picking up the ball (roadblock), detect irregularities in the line
def detect_crosswalk(state):
    global recently_added, program_position, NORMAL_SPEED
    if program_position == 2:
        #debug_print(last_three_white_passages)
        #debug_print(recently_added)
        #debug_print(is_color_white(COLOR_MIDDLE))
        #debug_print("sensors:", LIGHT_LEFT.value(), COLOR_MIDDLE.value(), LIGHT_RIGHT.value())
        if not recently_added and is_color_white(COLOR_MIDDLE) and is_light_white(LIGHT_LEFT) and is_light_white(LIGHT_RIGHT) and not state in ["offtrack-left", "offtrack-right"]:
            add_new_white_passage()
            recently_added = True
        if not is_color_white(COLOR_MIDDLE) or not is_color_white(LIGHT_LEFT) or not is_color_white(LIGHT_RIGHT):
            recently_added = False
        if (last_three_white_passages[0] - last_three_white_passages[1]) < 1.5:
            #debug_print(last_three_white_passages)
            #debug_print(last_three_white_passages[0] - last_three_white_passages[2])
            #debug_print(is_color_white(COLOR_MIDDLE))
            NORMAL_SPEED = math.floor(NORMAL_SPEED * 1.25)
            drive.on_for_rotations(left_speed=50, right_speed=-50, rotations=0.5)
            drive.on_for_seconds(NORMAL_SPEED, NORMAL_SPEED, 0.25)
            program_position = 3
            soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")


# After turning onto the T-crossing, push block and do a U-Turn
def push_block():
    global program_position, block_pushed
    if program_position == 3:
        while(get_distance() < 15):
            state = line_correction_needed()
            correct_path(state)
            block_pushed = True
        if block_pushed:
            drive.on_for_seconds(-30, -30, 1)
            drive.on_for_rotations(left_speed=-50, right_speed=50, rotations=1)
            program_position = 4
            soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")

# After pushing the block, return to line and turn right
def get_back_on_track(state):
    global program_position, back_on_track_reached
    if program_position == 4:
        while is_color_white(COLOR_MIDDLE) and is_light_white(LIGHT_LEFT) and is_light_white(LIGHT_RIGHT) and state != "offtrack-left" and state != "offtrack-right":
            drive.on(NORMAL_SPEED, NORMAL_SPEED)
            back_on_track_reached = True
        if back_on_track_reached:
            drive.on_for_rotations(left_speed=50, right_speed=-50, rotations=0.5)
            drive.on_for_seconds(NORMAL_SPEED, NORMAL_SPEED, 0.25)
            program_position = 5
            soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")
    

# Ending the program with the ball
def ball_dropoff(state):
    global program_position, ball_dropoff_detected
    if program_position == 5:
        if not is_color_white(COLOR_MIDDLE) and not is_light_white(LIGHT_LEFT) and not is_light_white(LIGHT_RIGHT):
            ball_dropoff_detected = True
        if ball_dropoff_detected and state != "offtrack-left" and state != "offtrack-right":
            while True:
                state = line_correction_needed()
                correct_path(state)
                if get_distance() < 4:
                    drive.off()
                    MOTOR_BASKET.on_for_seconds(10, 0.5)
                    MOTOR_BASKET.on_for_degrees(-5, 78)
                    return True
    return False


# Main program starts here.
# Reset basket
MOTOR_BASKET.on_for_seconds(10, 0.75)
MOTOR_BASKET.on_for_degrees(-10, 40)

# Main execution loop
while True:
    state = line_correction_needed()
    get_back_on_track(state)
    correct_path(state)

    # debug_print(program_position)

    wait_on_roadblock()
    detect_crosswalk(state)
    push_block()
    if ball_dropoff(state):
        soundemitter.tone(1500, 500, play_type="PLAY_NO_WAIT_FOR_COMPLETE")
        break