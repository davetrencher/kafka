from kafka.vessels.BaseVessel import BaseVessel

class SaturnV(BaseVessel):

    def describe(self):
        super(SaturnV,self).describe();

    def booster_stage(self):
        return 11;

