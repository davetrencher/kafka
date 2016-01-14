import krpc
import time
import math

#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html

turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

conn = krpc.connect(name='Hello World')

vessel = conn.space_center.active_vessel

ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
eccentricity = conn.add_stream(getattr, vessel.orbit, 'eccentricity')
#stage_2_resources = vessel.resources_in_decouple_stage(stage=2, cumulative=False)
#stage_3_resources = vessel.resources_in_decouple_stage(stage=3, cumulative=False)
#srb_fuel = conn.add_stream(stage_3_resources.amount, 'SolidFuel')
#launcher_fuel = conn.add_stream(stage_2_resources.amount, 'LiquidFuel')

print(vessel.name)

vessel.control.sas = False;
vessel.control.sas = True;
vessel.control.throttle = 1;

# Countdown...
print('3...'); time.sleep(1)
print('2...'); time.sleep(1)
print('1...'); time.sleep(1)
print('Launch!')

vessel.control.activate_next_stage();

vessel.auto_pilot.engage();
vessel.auto_pilot.target_pitch_and_heading(90, 90);

turn_angle=0;

while True:

    #Gravity Turn
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = (altitude() - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
        new_turn_angle = frac * 90

        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90-turn_angle,90)

    if apoapsis() > target_altitude*0.9:
        print('Approaching target apoapsis')
        break\

#power down when approaching target altitude
vessel.control.throttle = 0.25;
while apoapsis < target_altitude:
    pass

#throttle off
print("Target altitude reached")
vessel.control.throttle = 0;

# Wait until out of atmosphere
print('Coasting out of atmosphere')
while altitude() < 70500:
    pass

#time for circularisation burn;
print('Planning circularisation burn')
mu = vessel.orbit.body.gravitational_parameter;
r = vessel.orbit.apoapsis;
a = vessel.orbit.semi_major_axis;
G = vessel.orbit.body.gravitational_parameter
