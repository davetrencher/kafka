from kafka.vessels.BaseVessel import BaseVessel

class CommsSatLauncher(BaseVessel):

    def describe(self):
        super(CommsSatLauncher,self).describe();

    def booster_stage(self):
        return 6;


    def min_booster_fuel(self):
        return 70.1;

