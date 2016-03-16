from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.BaseVessel import BaseVessel

conn = KrpcHelper.conn

vessels = conn.space_center.vessels
vessel = BaseVessel(conn.space_center.active_vessel)
print(vessel.describe())

print("Welcome to Control");

conn.space_center.clear_target()
for avail_vessel in conn.space_center.vessels:
    print(avail_vessel.name)

