import time
import math

from kafka.helper.krpchelper import KrpcHelper
from kafka.helper.Logger import Logger
from kafka.launch.LaunchControl import LaunchControl

class OrbitalManouver:

    conn = KrpcHelper.conn

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

    def calculate_delta_v(self, apoapse_required):

        #vis viva equation
        mu = self.vessel.orbit.body.gravitational_parameter
        r = self.vessel.orbit.apoapsis
        a1 = self.vessel.orbit.semi_major_axis
        a2 = apoapse_required
        v1 = math.sqrt(mu*((2./r)-(1./a1))) #current velocity
        v2 = math.sqrt(mu*((2./r)-(1./a2))) #final velocity
        delta_v = v2 -v1 #velocity change to reach

        return delta_v

    def calculate_burn_time(self, delta_v):
        #rocket equation
        F = self.vessel.available_thrust
        isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass                #initial total mass including propellant
        m1 = m0 / math.exp(delta_v/isp) #dry mass no propellant
        flow_rate = F / isp
        burn_time = (m0 - m1) / flow_rate

        return burn_time

    def calculate_remaining_stage_delta_v(self):
        # rocket equation
        isp = self.vessel.specific_impulse
        m0 = self.vessel.mass  # initial total mass including propellant
        m1 = m0 - self.remaining_stage_fuel_weight() # dry mass decouple stage fuel burnt
        Logger.log(m0)
        Logger.log(m1)
        Logger.log(isp)
        delta_v = math.log(m0 / m1) * isp * 9.81

        return delta_v

    def remaining_stage_fuel_weight(self):
        return self.decorated.get_total_decouple_stage_fuel() / 0.2

    def orientate_vessel_for_burn(self,node, direction):
        Logger.log("Orientating ship for circularising burn")
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0,1,0)

        Logger.log(self.vessel.auto_pilot.target_direction)

    def wait_for_manouver_time(self, burn_time):
        Logger.log("Waiting until circularising burn")
        burn_ut = KrpcHelper.ut() + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        lead_time = 5
        OrbitalManouver.conn.space_center.warp_to(burn_ut - lead_time)
        Logger.log('Ready to execute burn')
        time_to_apoapsis = OrbitalManouver.conn.add_stream(getattr, self.vessel.orbit, 'time_to_apoapsis')
        while time_to_apoapsis() - (burn_time / 2.) > 0:
            pass

    def perform_manouver(self, burn_time, node):
        Logger.log('Executing burn')
        self.vessel.control.throttle = 1
        time.sleep(burn_time - 0.1)
        Logger.log('Fine tuning')
        self.vessel.control.throttle = 0.05
        remaining_burn = OrbitalManouver.conn.add_stream(node.remaining_burn_vector, node.reference_frame)
        while remaining_burn()[1] > 0:
            pass
        self.vessel.control.throttle = 0
        node.remove()

    def perform_orbit_circularisation(self):
        #time for circularisation burn;
        Logger.log('Planning circularising burn')

        delta_v = self.calculate_delta_v(self.vessel.orbit.apoapsis)
        stage_delta_v = self.calculate_remaining_stage_delta_v()

        Logger.log("Reqd Delta V: {} Remaining Stage Delta V: {}".format(delta_v,stage_delta_v))
        if stage_delta_v < delta_v:
            LaunchControl.abort()
            self.decorated.stage()
            delta_v = self.calculate_delta_v(self.vessel.orbit.apoapsis)

        node = self.vessel.control.add_node(KrpcHelper.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        burn_time = self.calculate_burn_time(delta_v)

        self.orientate_vessel_for_burn(node,(0,1,0))
        self.wait_for_manouver_time(burn_time)# Execute burn
        self.perform_manouver(burn_time, node)



    def perform_orbit_altitude_change(self, required_altitude):

        delta_v = self.calculate_delta_v(required_altitude)
        node = self.vessel.control.add_node(KrpcHelper.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        burn_time = self.calculate_burn_time(delta_v)
        Logger.log(node.burn_vector())
        self.orientate_vessel_for_burn(node, node.burn_vector())
        self.wait_for_manouver_time(burn_time)
        self.perform_manouver(burn_time, node)








