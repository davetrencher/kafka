from kafka.helper.krpchelper import KrpcHelper

class Logger:

    @staticmethod
    def log(message):

        vessel = KrpcHelper.conn.space_center.active_vessel
        if vessel.met > 0:
            print("T+{:.2f}: {}".format(vessel.met,message))
        else:
            print("Preflight: ",message)
