

class Logger:

    def log(vessel,  message):
        if (vessel.met > 0):
            print("T+{:.2f}: {}".format(vessel.met,message))
        else:
            print("Preflight: ",message)