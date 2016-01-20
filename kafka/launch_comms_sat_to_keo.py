#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
from kafka.launch.LaunchControl import LaunchControl
from kafka.orbital.OrbitalManouver import OrbitalManouver
from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.CommsSatLauncher import CommsSatLauncher

low_orbit_throttle = 0.5
turn_start_altitude = 250
turn_end_altitude = 65000
target_altitude = 120000

print("launching comms satellite")

conn = KrpcHelper.conn;

conn.space_center.clear_target()
# for avail_vessel in conn.space_center.vessels:
#     print(avail_vessel.name)

#conn.space_center.launch_vessel_from_vab("Apollo")

vessel = CommsSatLauncher(conn.space_center.active_vessel)
print(vessel.describe())

launchControl = LaunchControl(vessel)
#launchControl.activate(low_orbit_throttle)
#launchControl.gravityTurn(turn_start_altitude,turn_end_altitude,target_altitude)

launchControl.engage_autopilot()
orbitalManouver = OrbitalManouver(vessel)
orbitalManouver.perform_orbit_circularisation()

print('Launch complete')


