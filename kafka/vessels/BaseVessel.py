
from kafka.helper.krpchelper import KrpcHelper

class BaseVessel(object):

    def __init__(self, vessel):
        self.vessel = vessel

        self.altitude = KrpcHelper.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        liquid_booster_resources = self.vessel.resources_in_decouple_stage(stage=self.booster_stage(), cumulative=False) #4
        solid_booster_resources = self.vessel.resources_in_decouple_stage(stage=self.booster_stage(), cumulative=False) #4

        self.liquid_booster_fuel = KrpcHelper.conn.add_stream(liquid_booster_resources.amount, 'LiquidFuel')
        self.solid_booster_fuel = KrpcHelper.conn.add_stream(solid_booster_resources.amount, 'SolidFuel')
        print(self.liquid_booster_fuel())
        self.apoapsis = KrpcHelper.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')


    def describe(self):
        print("Name:", self.vessel.name)
        print("Type: ",self.vessel.type)
        print("Situ: ",self.vessel.situation)
        print("Boost: ",self.describe_decouple_stages())
        self.describe_thrust()

    def describe_thrust(self):
        print("Mass: ",)


        wetMass = self.vessel.mass
        weight = wetMass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.available_thrust
        max_thrust = self.vessel.max_thrust
        thrust = self.vessel.thrust
        twr = avail_thrust / weight

        print("{:.2f}: {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(self.altitude(),wetMass,avail_thrust,max_thrust,thrust,twr, self.booster_fuel()))

      #  print("Decouple stages ",self.describe_decouple_stages());

    def describe_decouple_stages(self):
         for el in self.get_decouple_stages():
            resource = self.vessel.resources_in_decouple_stage(stage=el, cumulative=False)

            if resource.has_resource("LiquidFuel"):
                print("Resources in stage: [%s] Liquid Fuel: ",el, resource.amount("LiquidFuel"))

            if resource.has_resource("SolidFuel"):
                print("Resources in stage: [%s] Solid Booster: ",el, resource.amount("SolidFuel"))

    def booster_fuel(self):
        return self.liquid_booster_fuel() + self.solid_booster_fuel()


    def stage(self):
        self.vessel.control.activate_next_stage()
        print("activating stage: ", self.vessel.control.current_stage)

    def booster_stage(self):
        return -1;

    def min_booster_fuel(self):
        return 0.1;

    def get_decouple_stages(self):

        decoupleStages = set()
        for el in self.vessel.parts.all:
            decoupleStages.add(el.decouple_stage)

        return sorted(decoupleStages)

    def retract_launchtowers(self):
        pass

    def disengage_launch_clamps(self):
        for el in self.vessel.parts.launch_clamps:
            el.release()

