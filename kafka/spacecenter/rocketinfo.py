from kafka.helper.krpchelper import KrpcHelper
from kafka.vessels.Apollo import Apollo
from kafka.vessels.SaturnV import SaturnV


conn = KrpcHelper.conn

vessels = conn.space_center.vessels


vessel = SaturnV(conn.space_center.active_vessel)
print(vessel.describe())

print("Welcome to Control");

