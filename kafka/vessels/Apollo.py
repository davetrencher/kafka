from kafka.vessels.BaseVessel import BaseVessel

class Apollo(BaseVessel):

    def describe(self):
        super(Apollo,self).describe();

    def booster_stage(self):
        return 5;

