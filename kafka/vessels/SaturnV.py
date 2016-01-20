from kafka.vessels.BaseVessel import BaseVessel

class SaturnV(BaseVessel):

    def describe(self):
        super(SaturnV,self).describe();



    def retract_launchtowers(self):
        super(SaturnV,self).retract_launchtowers()
        self.vessel.control.activate_next_stage();

    def booster_stage(self):
        return 9;

