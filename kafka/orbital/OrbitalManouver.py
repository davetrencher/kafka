import time
import math

from kafka.helper.krpchelper import KrpcHelper

class OrbitalManouver:

    conn = KrpcHelper.conn
    ut = conn.add_stream(getattr, conn.space_center, 'ut')

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

    def calculate_delta_v(self, apoapse_required):

        #vis viva equation
        mu = self.vessel.orbit.body.gravitational_parameter;
        r = self.vessel.orbit.apoapsis;
        a1 = self.vessel.orbit.semi_major_axis;
        a2 = apoapse_required;
        v1 = math.sqrt(mu*((2./r)-(1./a1))) #current velocity
        v2 = math.sqrt(mu*((2./r)-(1./a2))) #final velocity
        delta_v = v2 -v1 #velocity change to reach

        return delta_v

    def calculate_burn_time(self, delta_v):
        #rocket equation
        F = self.vessel.available_thrust
        Isp = self.vessel.specific_impulse * 9.82
        m0 = self.vessel.mass                #initial total mass including propellant
        m1 = m0 / math.exp(delta_v/Isp) #dry mass no propellant
        flow_rate = F / Isp
        burn_time = (m0 - m1) / flow_rate

        return burn_time

    def orientate_vessel_for_burn(self,node, direction):
        print("Orientating ship for circularisation burn")
        self.vessel.auto_pilot.engage()
        self.vessel.auto_pilot.reference_frame = node.reference_frame
        self.vessel.auto_pilot.target_direction = (0,1,0)
        self.vessel.auto_pilot.wait
        print(self.vessel.auto_pilot.target_direction)

    def wait_for_manouver_time(self, burn_time):
        print("Waiting until circularisation burn")
        burn_ut = OrbitalManouver.ut() + self.vessel.orbit.time_to_apoapsis - (burn_time / 2.)
        lead_time = 5
        OrbitalManouver.conn.space_center.warp_to(burn_ut - lead_time)
        print('Ready to execute burn')
        time_to_apoapsis = OrbitalManouver.conn.add_stream(getattr, self.vessel.orbit, 'time_to_apoapsis')
        while time_to_apoapsis() - (burn_time / 2.) > 0:
            pass

    def perform_manouver(self, burn_time, node):
        print('Executing burn')
        self.vessel.control.throttle = 1
        time.sleep(burn_time - 0.1)
        print('Fine tuning')
        self.vessel.control.throttle = 0.05
        remaining_burn = OrbitalManouver.conn.add_stream(node.remaining_burn_vector, node.reference_frame)
        while remaining_burn()[1] > 0:
            pass
        self.vessel.control.throttle = 0
        node.remove()

    def perform_orbit_circularisation(self):
        #time for circularisation burn;
        print('Planning circularisation burn')

        delta_v = self.calculate_delta_v(self.vessel.orbit.apoapsis);
        node = self.vessel.control.add_node(OrbitalManouver.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        burn_time = self.calculate_burn_time(delta_v)

        self.orientate_vessel_for_burn(node,(0,1,0))
        self.wait_for_manouver_time(burn_time)# Execute burn
        self.perform_manouver(burn_time, node)



    def perform_orbit_altitude_change(self, required_altitude):

        delta_v = self.calculate_delta_v(required_altitude);
        node = self.vessel.control.add_node(OrbitalManouver.ut() + self.vessel.orbit.time_to_apoapsis, prograde=delta_v)

        burn_time = self.calculate_burn_time(delta_v)
        print(node.burn_vector())
        self.orientate_vessel_for_burn(node, node.burn_vector())
        self.wait_for_manouver_time(burn_time)
        self.perform_manouver(burn_time, node)








