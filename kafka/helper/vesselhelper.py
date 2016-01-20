from kafka.helper.krpchelper import KrpcHelper

class VesselHelper:

    conn = KrpcHelper.conn

    vessel = conn.space_center.active_vessel




