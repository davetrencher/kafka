#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
import time

from kafka.launch.LaunchControl import LaunchControl
from kafka.orbital.OrbitalManouver import OrbitalManouver
from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.CommsSatLauncher import BaseVessel

low_orbit_throttle = 1
turn_start_altitude = 500
turn_end_altitude = 45000
target_altitude = 150000

print("launching comms satellite")

conn = KrpcHelper.conn;

conn.space_center.clear_target()

vessel = BaseVessel(conn.space_center.active_vessel)
print(vessel.describe())

launchControl = LaunchControl(vessel)
launchControl.activate(low_orbit_throttle)
launchControl.gravityTurn(turn_start_altitude,turn_end_altitude,target_altitude)

launchControl.engage_autopilot()

vessel.deploy_fairings()
time.sleep(4)

vessel.deploy_solar_panels()
time.sleep(10)
vessel.vessel.control.set_action_group(2,True)
print('activated action group 2')

launchControl.engage_autopilot()
orbitalManouver = OrbitalManouver(vessel)
orbitalManouver.perform_orbit_circularisation()

orbitalManouver.perform_orbit_altitude_change(1200000)
orbitalManouver.perform_orbit_circularisation()


print('Launch complete')


