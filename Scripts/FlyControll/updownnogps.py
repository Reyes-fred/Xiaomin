#!/usr/bin/env python2.7
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil
import time
import math
import os
import threading

current_thrust = 0.5

# Connect to the Vehicle
vehicle = connect(os.environ['protocol']+":"+os.environ['ip']+":"+os.environ['port'], wait_ready=True)

def arm_and_takeoff_nogps(aTargetAltitude):

    global current_thrust

    ##### CONSTANTS #####
    DEFAULT_TAKEOFF_THRUST = 0.65
    SMOOTH_TAKEOFF_THRUST = 0.55

    print("Basic pre-arm checks")
    # Don't let the user try to arm until autopilot is ready
    # If you need to disable the arming check,
    # just comment it with your own responsibility.
    #while not vehicle.is_armable:
    #    print(" Waiting for vehicle to initialise...")
    #    time.sleep(1)


    print("Arming motors")
    # Copter should arm in GUIDED_NOGPS mode
    vehicle.mode = VehicleMode("GUIDED_NOGPS")
    vehicle.armed = True

    while not vehicle.armed:
        print(" Waiting for arming...")
        vehicle.armed = True
        time.sleep(1)

    print("Taking off!")

    current_thrust = DEFAULT_TAKEOFF_THRUST
    while True:
	current_altitude = vehicle.location.global_relative_frame.alt
	print(current_altitude)
	print(aTargetAltitude)
        if current_altitude >= aTargetAltitude*0.8: # Trigger just below target alt.
            print("Reached target altitude")
            current_thrust = 0.5
            break
        elif current_altitude >= aTargetAltitude*0.6:
            current_thrust = SMOOTH_TAKEOFF_THRUST
        set_attitude()
        time.sleep(0.2)

def send_attitude_target(roll_angle = 0.0, pitch_angle = 0.0,
                         yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = True):
    """
    use_yaw_rate: the yaw can be controlled using yaw_angle OR yaw_rate.
                  When one is used, the other is ignored by Ardupilot.
    thrust: 0 <= thrust <= 1, as a fraction of maximum vertical thrust.
            Note that as of Copter 3.5, thrust = 0.5 triggers a special case in
            the code for maintaining current altitude.
    """
    
    global current_thrust
    
    if not use_yaw_rate and yaw_angle is None:
        yaw_angle = vehicle.attitude.yaw

    if yaw_angle is None:
        yaw_angle = 0.0
    
    # Thrust >  0.5: Ascend
    # Thrust == 0.5: Hold the altitude
    # Thrust <  0.5: Descend
    msg = vehicle.message_factory.set_attitude_target_encode(
        0, # time_boot_ms
        1, # Target system
        1, # Target component
        0b00000000 if use_yaw_rate else 0b00000100,
        to_quaternion(roll_angle, pitch_angle, yaw_angle), # Quaternion
        0, # Body roll rate in radian
        0, # Body pitch rate in radian
        math.radians(yaw_rate), # Body yaw rate in radian/second
        current_thrust  # Thrust
    )
    vehicle.send_mavlink(msg)

def set_attitude(roll_angle = 0.0, pitch_angle = 0.0,
                 yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = True,
                 duration = 0):
    """
    Note that from AC3.3 the message should be re-sent more often than every
    second, as an ATTITUDE_TARGET order has a timeout of 1s.
    In AC3.2.1 and earlier the specified attitude persists until it is canceled.
    The code below should work on either version.
    Sending the message multiple times is the recommended way.
    """

    send_attitude_target(roll_angle, pitch_angle,
                         yaw_angle, yaw_rate, use_yaw_rate)
    start = time.time()
    while time.time() - start < duration:
        send_attitude_target(roll_angle, pitch_angle,
                             yaw_angle, yaw_rate, use_yaw_rate)
        time.sleep(0.01)
    # Reset attitude, or it will persist for 1s more due to the timeout
    send_attitude_target(0, 0,
                         0, 0, True)

def to_quaternion(roll = 0.0, pitch = 0.0, yaw = 0.0):
    """
    Convert degrees to quaternions
    """
    t0 = math.cos(math.radians(yaw * 0.5))
    t1 = math.sin(math.radians(yaw * 0.5))
    t2 = math.cos(math.radians(roll * 0.5))
    t3 = math.sin(math.radians(roll * 0.5))
    t4 = math.cos(math.radians(pitch * 0.5))
    t5 = math.sin(math.radians(pitch * 0.5))

    w = t0 * t2 * t4 + t1 * t3 * t5
    x = t0 * t3 * t4 - t1 * t2 * t5
    y = t0 * t2 * t5 + t1 * t3 * t4
    z = t1 * t2 * t4 - t0 * t3 * t5

    return [w, x, y, z]

def altitude_holder(target_altitude):
    ACCEPTABLE_ALTITUDE_ERROR = 0.15
    global current_thrust
    
    print("Altitdude holer started")
    while(vehicle.mode != "LAND"):
        current_altitude = vehicle.location.global_relative_frame.alt
        #print(" Altitude: %f Target Altitude: %f " % (current_altitude, target_altitude))
        print " Attitude: %s" % vehicle.attitude
        #print " Velocity: %s" % vehicle.velocity
        #print " Groundspeed: %s" % vehicle.groundspeed    # settable

        if(current_altitude < target_altitude - ACCEPTABLE_ALTITUDE_ERROR):
            current_thrust += 0.01
            current_thrust = 0.65 if current_thrust > 0.65 else current_thrust
            print("THRUST UP")
        elif(current_altitude > target_altitude + ACCEPTABLE_ALTITUDE_ERROR):
            current_thrust -= 0.01
            current_thrust = 0.35 if current_thrust < 0.35 else current_thrust
            print("THRUST DOWN")
        else:
            current_thrust = 0.5
            print("THRUST HOLD")

        #set_thrust(current_thrust)
        time.sleep(0.1)

# Take off 2.5m in GUIDED_NOGPS mode.
           

arm_and_takeoff_nogps(1.0)

t = threading.Thread(target=altitude_holder, args=(TARGET_ALTITUDE,))
t.daemon = True
t.start()

# Hold the position for 3 seconds.
print("Hold position for 3 seconds")
set_attitude(duration = 3)

# Uncomment the lines below for testing roll angle and yaw rate.
# Make sure that there is enough space for testing this.

# set_attitude(roll_angle = 1, thrust = 0.5, duration = 3)
# set_attitude(yaw_rate = 30, thrust = 0.5, duration = 3)

# Move the drone forward and backward.
# Note that it will be in front of original position due to inertia.
print("Move forward")
set_attitude(pitch_angle = -5, duration = 3.21)

print("Move backward")
set_attitude(pitch_angle = 5, duration = 3)


print("Setting LAND mode...")
vehicle.mode = VehicleMode("LAND")
time.sleep(1)

# Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()

print("Completed")

