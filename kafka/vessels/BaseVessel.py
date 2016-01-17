

class BaseVessel(object):

    def booster_stage(self):
        return -1;

    def __init__(self, vessel):
        self.vessel = vessel

