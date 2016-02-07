#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
from kafka.launch.LaunchControl import LaunchControl
from kafka.orbital.OrbitalManouver import OrbitalManouver
from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.CommsSatLauncher import CommsSatLauncher

low_orbit_throttle = 1
turn_start_altitude = 500
turn_end_altitude = 45000
target_altitude = 150000

print("launching comms satellite")

conn = KrpcHelper.conn;

conn.space_center.clear_target()

vessel = CommsSatLauncher(conn.space_center.active_vessel)
print(vessel.describe())

launchControl = LaunchControl(vessel)
launchControl.activate(low_orbit_throttle)
launchControl.gravityTurn(turn_start_altitude,turn_end_altitude,target_altitude)

launchControl.engage_autopilot()

if vessel.vessel.control.get_action_group(0) == False:
    vessel.vessel.control.set_action_group(0,True)
    print('activated action group 0')
    vessel.vessel.control.set_action_group(1,True)
    print('activated action group 1')

orbitalManouver = OrbitalManouver(vessel)
orbitalManouver.perform_orbit_circularisation()

print('Launch complete')


