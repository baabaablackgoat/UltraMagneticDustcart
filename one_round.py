#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, MoveTank, Motor

MoveTank(OUTPUT_A, OUTPUT_B).on_for_rotations(30,30,1)