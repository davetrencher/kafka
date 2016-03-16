import logging
import os

from kafka.helper.krpchelper import KrpcHelper

class BaseVessel(object):

    def __init__(self, vessel):
        self.vessel = vessel
        self.info = BaseVesselInfo(self)
        self.initialise_streams()

    def initialise_streams(self):
        self.altitude = KrpcHelper.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = KrpcHelper.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')

        self.decouple_stage_liquid_streams = {}
        self.decouple_stage_solid_streams = {}
        for decouple_stage in self.list_decouple_stages():
            self.create_resource_stream(decouple_stage,'LiquidFuel')
            self.create_resource_stream(decouple_stage,'SolidFuel')


    def create_resource_stream(self,decouple_stage, resource_name):

        stream_list = self.get_streams_for_resource(resource_name)

        resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False) #4
        if resources.max(resource_name) > 0.0:
            stream_list[decouple_stage] =  KrpcHelper.conn.add_stream(resources.amount,resource_name);

    def describe(self):
        self.info.describe();

    def log_flight_data(self):
        self.info.log_flight_data();

    def twr(self):
        wetMass = self.vessel.mass
        weight = wetMass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.thrust

        return avail_thrust / weight

    def is_decouple_stage_resources_exhausted(self, decouple_stage):

        if (self.is_decouple_stage_resource_exhausted(decouple_stage,"LiquidFuel")) \
                or (self.is_decouple_stage_resource_exhausted(decouple_stage,"SolidFuel")):
            return True

        return False

    def is_decouple_stage_resource_exhausted(self,decouple_stage, resource_name):

        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False)
        resource_streams = self.get_streams_for_resource(resource_name)

        if (decouple_stage in resource_streams.keys()):
            fuel_max = decouple_stage_resources.max(resource_name)

            fuel_amount = resource_streams[decouple_stage]()

            if fuel_max > 0.0 and fuel_amount < 0.2:
                return True

        return False


    def get_streams_for_resource(self,resource_name):

        return {
            'LiquidFuel' : self.decouple_stage_liquid_streams,
            'SolidFuel'  : self.decouple_stage_solid_streams
        }.get(resource_name)

    def decouple_stage_fuel(self,name):

        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=self.current_decouple_stage(), cumulative=False) #4
        liquid_fuel_amount = decouple_stage_resources.amount(name)

        return liquid_fuel_amount

    def current_decouple_stage(self):
        return self.list_decouple_stages()[-1]


    def stage(self):
        self.vessel.control.activate_next_stage()
        print("activating stage: ", self.vessel.control.current_stage)

    def list_decouple_stages(self):

        decoupleStages = set()
        for part in self.vessel.parts.all:
            decoupleStages.add(part.decouple_stage+1)

        return sorted(decoupleStages)

    def disengage_launch_clamps(self):
        for el in self.vessel.parts.launch_clamps:
            print("Disengaging Launch Clamps")
            el.release()
            print("Disengaged Launch Clamps")

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

                print("deploying fairings")

                module.trigger_event('Deploy')

                print("deployed fairings")


    def deploy_solar_panels(self):
        for solar_panel in self.vessel.parts.solar_panels:
            print("deploying solar panels")
            solar_panel.deployed = True
            print("deployed solar panels")


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
        for stage_id in sorted(decouple_stages):
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

        status = "{:.2f}: {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(self.vessel.met, self.decorated.altitude(),wetMass,avail_thrust,max_thrust,thrust,twr, self.decorated.decouple_stage_fuel("LiquidFuel"),self.decorated.decouple_stage_fuel("SolidFuel"))

        logging.debug(status)




