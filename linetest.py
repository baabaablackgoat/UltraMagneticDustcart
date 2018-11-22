#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor
import sys
def debug_print(*args, **kwargs):
    '''Print debug messages to stderr.

    This shows up in the output panel in VS Code.
    '''
    print(*args, **kwargs, file=sys.stderr)

motora = Motor(OUTPUT_A)

while True:
    if not motora.is_running:
        motora.on(20)
    motora.stop()

    