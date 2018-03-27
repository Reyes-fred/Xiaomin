#!/usr/bin/python
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import os

vehicle = connect(os.environ['protocol']+":"+os.environ['ip']+":"+os.environ['port'], wait_ready=False)
print("Arming motors:")
vehicle.mode    = VehicleMode("GUIDED")
vehicle.armed   = True
while not vehicle.armed:
        print(" Waiting for arming to be finished")
        time.sleep(1)
print("Keeping motors armed for 5s")
time.sleep(5)
print("Disarming")
vehicle.armed   = False
