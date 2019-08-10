import logging
import os

from kafka.helper.krpchelper import KrpcHelper
from kafka.helper.Logger import Logger

from enum import Enum

class FuelType(Enum):
    LIQUID_FUEL = 'LiquidFuel'
    SOLID_FUEL = 'SolidFuel'
    OXIDIZER = 'Oxidizer'

class BaseVessel(object):

    supported_fuel_types = [FuelType.LIQUID_FUEL,
                            FuelType.OXIDIZER,
                            FuelType.SOLID_FUEL]

    def __init__(self, vessel):
        self.vessel = vessel
        self.info = BaseVesselInfo(self)

        self.altitude = KrpcHelper.conn.add_stream(getattr, self.vessel.flight(), 'mean_altitude')
        self.apoapsis = KrpcHelper.conn.add_stream(getattr, self.vessel.orbit, 'apoapsis_altitude')
        self.decouple_stage_liquid_streams = {}
        self.decouple_stage_oxidizer_streams = {}
        self.decouple_stage_solid_streams = {}

        for decouple_stage in self.list_decouple_stages():
            self.create_resource_stream(decouple_stage,FuelType.LIQUID_FUEL)
            self.create_resource_stream(decouple_stage,FuelType.OXIDIZER)
            self.create_resource_stream(decouple_stage,FuelType.SOLID_FUEL)

    def create_resource_stream(self,decouple_stage, fuel_type):

        stream_list = self.get_streams_for_resource(fuel_type)

        resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False) #4

        if resources.has_resource(fuel_type.value) is True:
            stream_list[decouple_stage] =  KrpcHelper.conn.add_stream(resources.amount,fuel_type.value)

    def describe(self):
        self.info.describe()

    def log_flight_data(self):
        self.info.log_flight_data()

    def set_throttle(self,throttle):
        self.vessel.control.throttle = float(throttle)
        Logger.log("Throttle set to {:.2f}".format(float(throttle)))

    def twr(self):
        wet_mass = self.vessel.mass
        weight = wet_mass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.thrust

        return avail_thrust / weight

    def max_stage_twr(self):
        wet_mass = self.vessel.mass
        weight = wet_mass * 9.81  # kerbin gravity
        max_thrust = self.vessel.max_thrust

        return max_thrust / weight

    def is_decouple_stage_resources_exhausted(self, decouple_stage = None):

        if decouple_stage is None:
            decouple_stage = self.current_decouple_stage()

        if (self.is_decouple_stage_resource_exhausted(decouple_stage,FuelType.LIQUID_FUEL)) \
                and (self.is_decouple_stage_resource_exhausted(decouple_stage,FuelType.SOLID_FUEL)):
            return True

        return False

    def is_decouple_stage_resource_exhausted(self,decouple_stage, fuel_type):

        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=decouple_stage, cumulative=False)
        resource_streams = self.get_streams_for_resource(fuel_type)

        if decouple_stage in resource_streams.keys():
            fuel_max = decouple_stage_resources.max(fuel_type.value)

            fuel_amount = resource_streams[decouple_stage]()

            if fuel_max > 0.0 and fuel_amount > 0.2:
                return False

        return True

    def get_streams_for_resource(self,fuel_type):

        return {
            FuelType.LIQUID_FUEL: self.decouple_stage_liquid_streams,
            FuelType.OXIDIZER: self.decouple_stage_oxidizer_streams,
            FuelType.SOLID_FUEL : self.decouple_stage_solid_streams
        }.get(fuel_type)

    def decouple_stage_fuel(self,fuel_type):

        decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=self.current_decouple_stage(), cumulative=False) #4
        fuel_amount = decouple_stage_resources.amount(fuel_type.value)

        return fuel_amount

    def get_total_decouple_stage_fuel(self):
        total_units = 0
        for fuel_type in BaseVessel.supported_fuel_types:
            total_units += self.decouple_stage_fuel(fuel_type)

        return total_units

    def has_no_thrust(self):
        return self.vessel.thrust == 0.0 and self.vessel.control.throttle > 0.1

    def engines_in_current_stage(self):
        parts_in_current_stage = self.vessel.parts.in_stage(self.active_stage())
        engines = set()
        for part in parts_in_current_stage:
            if part.engine is not None:
                engines.add(part.engine)

        return engines

    def current_decouple_stage(self):
        return self.list_decouple_stages()[-1]

    def active_stage(self):
        return self.vessel.control.current_stage

    def stage(self):
        self.vessel.control.activate_next_stage()
        Logger.log("Activating stage: {}".format(self.active_stage()))

    def list_decouple_stages(self):

        decouple_stages = set()
        for part in self.vessel.parts.all:
            decouple_stages.add(part.decouple_stage)

        return sorted(decouple_stages)

    def  disengage_launch_clamps(self):
        for el in self.vessel.parts.launch_clamps:
            Logger.log("Disengaging Launch Clamps")
            el.release()
            Logger.log("Disengaged Launch Clamps")

    def deploy_fairings(self):

        parts = self.vessel.parts.all
        fairings = list(filter(lambda p: 'Fairing' in p.title, parts))

        for fairing in fairings:
            modules = list(filter(lambda m: m.name == 'ModuleProceduralFairing', fairing.modules))

            for module in modules:
                Logger.log(module.name)
                Logger.log("fields: {}".format(module.fields))
                Logger.log("events: {}".format(module.events))
                Logger.log("actions: {}".format(module.actions))

                Logger.log("deploying fairings")

                module.trigger_event('Deploy')

                Logger.log("deployed fairings")


    def deploy_solar_panels(self):
        for solar_panel in self.vessel.parts.solar_panels:
            Logger.log("deploying solar panels")
            solar_panel.deployed = True
            Logger.log("deployed solar panels")


from table_logger import TableLogger

class BaseVesselInfo(object):

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

        log_file = os.path.join(KrpcHelper.LOG_DIR, self.vessel.name + '.log')

        logging.basicConfig(filename=log_file, filemode='w+', level=logging.DEBUG)

    def describe(self):
        Logger.log("Name: {}".format(self.vessel.name))
        Logger.log("Type: {}".format(self.vessel.type))
        Logger.log("Situ: {}".format(self.vessel.situation))
        self.describe_decouple_stages()
        self.log_flight_data()
        parts = self.vessel.parts.all
        parts.sort(key = lambda part: part.stage)

        decouple_stages = set()

        tbl = TableLogger(columns='activated stage,decouple stage, part title, part name')
        for part in parts:
            tbl(part.stage,part.decouple_stage,part.title,part.name)
            decouple_stages.add(part.decouple_stage)


        Logger.log("Resources Per Stage:")
        for stage_id in sorted(decouple_stages):
            decouple_stage_resources = self.vessel.resources_in_decouple_stage(stage=stage_id, cumulative=False)
            resource_names = decouple_stage_resources.names
            tbl = TableLogger(columns='decouple stage,resource_name, amount/max')
            for resource_name in resource_names:
                tbl(stage_id,resource_name,"{:.2f}/{:.2f}".format(decouple_stage_resources.amount(resource_name),decouple_stage_resources.max(resource_name)))

        Logger.log("Parts:")
        parts.sort(key = lambda part: part.decouple_stage)
        tbl = TableLogger(columns='decouple stage, activated stage, title')
        for part in parts:
            tbl(part.decouple_stage,part.stage,part.title)


    def describe_decouple_stages(self):

        decouple_stages = self.decorated.list_decouple_stages()
        Logger.log(decouple_stages)
        for el in decouple_stages:

            resource = self.vessel.resources_in_decouple_stage(stage=el, cumulative=False)
            Logger.log("{} {}".format(el,resource.max(FuelType.LIQUID_FUEL.value)))


            if resource.has_resource(FuelType.LIQUID_FUEL.value):
                Logger.log("Resources in stage: [{}] Liquid Fuel: {}".format(el,resource.amount(FuelType.LIQUID_FUEL.value)))

            if resource.has_resource(FuelType.SOLID_FUEL.value):
                Logger.log("Resources in stage: [{}] Solid Booster: {}".format(el,resource.amount(FuelType.SOLID_FUEL.value)))

    def log_flight_data(self):
        wet_mass = self.vessel.mass
        weight = wet_mass * 9.81  #kerbin gravity
        avail_thrust = self.vessel.available_thrust
        max_thrust = self.vessel.max_thrust
        thrust = self.vessel.thrust
        twr = avail_thrust / weight

        status = "{:.2f}: {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}".format(self.vessel.met, self.decorated.altitude(),wet_mass,avail_thrust,max_thrust,thrust,twr, self.decorated.decouple_stage_fuel(FuelType.LIQUID_FUEL),self.decorated.decouple_stage_fuel(FuelType.SOLID_FUEL))

        logging.debug(status)

    def describe_current_stage_engines(self):
        engines = self.decorated.engines_in_current_stage()
        tbl = TableLogger(columns='engine, thrust, available_thrust, has fuel, is_active')
        for engine in engines:
            tbl(engine.part.name, engine.thrust, engine.available_thrust, engine.has_fuel, engine.active)

