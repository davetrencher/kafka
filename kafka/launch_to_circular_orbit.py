#http://djungelorm.github.io/krpc/docs/tutorials/launch-into-orbit.html
from kafka.launch.LaunchControl import LaunchControl
from kafka.orbital.OrbitalManouver import OrbitalManouver
from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.BaseVessel import BaseVessel
from kafka.helper.Logger import Logger
from kafka.helper.DateHelper import Date

turn_start_altitude = 250
turn_end_altitude = 65000
target_altitude = 120000

conn = KrpcHelper.conn;

vessel = BaseVessel(conn.space_center.active_vessel)
#vessel.describe()

launchTime = Date.get_instance_time_of_day(Date.NOON)
print("launch_time set to: {} ".format(Date.get_instance_from_seconds(launchTime).to_string()))
conn.space_center.warp_to(launchTime)

launchControl = LaunchControl(vessel)
launchControl.activate(3)
launchControl.gravityTurn(turn_start_altitude,turn_end_altitude,target_altitude)

orbitalManouver = OrbitalManouver(vessel)
orbitalManouver.perform_orbit_circularisation()

Logger.log('Launch complete')


