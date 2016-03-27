from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.BaseVessel import BaseVessel

conn = KrpcHelper.conn

vessels = conn.space_center.vessels
vessel = BaseVessel(conn.space_center.active_vessel)
Logger.log(vessel.describe())

Logger.log("Welcome to Control");

conn.space_center.clear_target()
for avail_vessel in conn.space_center.vessels:
    Logger.log(avail_vessel.name)

