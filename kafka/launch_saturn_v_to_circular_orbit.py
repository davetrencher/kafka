#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
from kafka.launch.LaunchControl import LaunchControl
from kafka.orbital.OrbitalManouver import OrbitalManouver
from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.BaseVessel import BaseVessel

low_orbit_throttle = 1.0
turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 120000

conn = KrpcHelper.conn;

vessel = BaseVessel(conn.space_center.active_vessel)
print(vessel.describe())

launchControl = LaunchControl(vessel)
launchControl.activate(low_orbit_throttle)
launchControl.gravityTurn(turn_start_altitude,turn_end_altitude,target_altitude)

orbitalManouver = OrbitalManouver(vessel)
orbitalManouver.perform_orbit_circularisation()

print('Launch complete')


