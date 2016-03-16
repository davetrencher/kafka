import logging
import os
from kafka.helper.krpchelper import KrpcHelper

class BaseVessel(object):

    def __init__(self, vessel):
        self.vessel = vessel
        self.info = BaseVesselInfo(self)

        self.altitude = KrpcHelper.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')

        #rewrite to get decouple stage resources and put in to map of some kind.
        self.decouple_stage_liquid_streams = {}
        for decouple_stage in self.list_decouple_stages():
            resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False) #4
            if resources.max("LiquidFuel") > 0.0:
                self.liquid_booster_fuel = KrpcHelper.conn.add_stream(resources.amount, 'LiquidFuel')
                self.decouple_stage_liquid_streams[decouple_stage] =  self.liquid_booster_fuel

            #add solid and electric at some point
            # id
            # self.solid_booster_fuel = KrpcHelper.conn.add_stream(liquid_booster_resources.amount, 'SolidFuel')


        self.apoapsis = KrpcHelper.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')

    def describe(self):
        self.info.describe();

    def log_flight_data(self):
        self.info.log_flight_data();

    def twr(self):
        wetMass = self.vessel.mass
        weight = wetMass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.thrust

        return avail_thrust / weight

    def decouple_stage_fuel_spent(self, decouple_stage):
        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False) #4

        liquid_fuel_max = decouple_stage_resources.max("LiquidFuel")
        liquid_fuel_amount = self.decouple_stage_liquid_streams[decouple_stage]()
        solid_fuel_max = decouple_stage_resources.max("SolidFuel")
        solid_fuel_amount = decouple_stage_resources.amount("SolidFuel")

        print(decouple_stage,': ',liquid_fuel_amount,"/",liquid_fuel_max)

        if liquid_fuel_max > 0.0 and liquid_fuel_amount < 0.2:
            return True;

        if solid_fuel_max > 0.0 and solid_fuel_amount < 0.2:
            return True;

        return False

    def decouple_stage_fuel(self,name):

        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=self.list_decouple_stages()[-1], cumulative=False) #4
        liquid_fuel_amount = decouple_stage_resources.amount(name)

        return liquid_fuel_amount



    def stage(self):
        self.vessel.control.activate_next_stage()
        print("activating stage: ", self.vessel.control.current_stage)

    def min_booster_fuel(self):
        return 0.1;

    def list_decouple_stages(self):

        decoupleStages = set()
        for part in self.vessel.parts.all:
            decoupleStages.add(part.decouple_stage+1)

        return sorted(decoupleStages)

    def disengage_launch_clamps(self):
        for el in self.vessel.parts.launch_clamps:
            el.release()

    def deploy_fairings(self):

        parts = self.vessel.parts.all
        fairings = list(filter(lambda p: 'Fairing' in p.title, parts))

        for fairing in fairings:
            modules = list(filter(lambda m: m.name == 'ModuleProceduralFairing', fairing.modules))

            for module in modules:
                print(module.name)
                print("fields: ", module.fields)
                print("events: ", module.events)
                print("actions: ", module.actions)

                module.trigger_event('Deploy')


    def deploy_solar_panels(self):
        for solar_panel in self.vessel.parts.solar_panels:
            print("deploying solar panels")
            solar_panel.deployed = True


class BaseVesselInfo(object):

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

        log_file = os.path.join(KrpcHelper.LOG_DIR, self.vessel.name + '.log');
        logging.basicConfig(filename=log_file, level=logging.DEBUG)

    def describe(self):
        print("Name:", self.vessel.name)
        print("Type: ",self.vessel.type)
        print("Situ: ",self.vessel.situation)
        print("Boost: ",self.describe_decouple_stages())
        self.log_flight_data()
        parts = self.vessel.parts.all
        parts.sort(key = lambda part: part.stage)

        decouple_stages = set()

        for part in parts:
            print(part.stage,' ',part.decouple_stage,' ',part.title,' ',part.name)
            decouple_stages.add(part.decouple_stage)


        print("decouple stages")
        for stage_id in [-1,1,2,3,4,5,6]:  #sorted(decouple_stages):
            decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=stage_id, cumulative=False)
            resource_names = decouple_stage_resources.names
            for resource_name in resource_names:
                print(stage_id,' ',resource_name,' ',decouple_stage_resources.amount(resource_name),' ',decouple_stage_resources.max(resource_name));

        parts.sort(key = lambda part: part.decouple_stage)
        for part in parts:
            print(part.stage,' ',part.decouple_stage,' ',part.title,' ',part.name)


    def describe_decouple_stages(self):

        decouple_stages = self.decorated.list_decouple_stages()
        print(decouple_stages)
        for el in decouple_stages:

            resource = self.vessel.resources_in_decouple_stage(stage=el, cumulative=False)
            print(el,' ',resource.max("LiquidFuel"))

            if resource.has_resource("LiquidFuel"):
                print("Resources in stage: [{}] Liquid Fuel: ".format(el), resource.amount("LiquidFuel"))

            if resource.has_resource("SolidFuel"):
                print("Resources in stage: [{}] Solid Booster: ".format(el), resource.amount("SolidFuel"))

    def log_flight_data(self):
        wetMass = self.vessel.mass
        weight = wetMass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.available_thrust
        max_thrust = self.vessel.max_thrust
        thrust = self.vessel.thrust
        twr = avail_thrust / weight

        status = "{:.2f}: {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(self.vessel.met, self.decorated.altitude(),wetMass,avail_thrust,max_thrust,thrust,twr, self.decorated.decouple_stage_fuel("LiquidFuel"))

        logging.debug(status)
