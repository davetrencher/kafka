import time

from kafka.helper.vesselhelper import VesselHelper


class LaunchControl:

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

    def preflight_setup(self,low_orbit_throttle):
        print(self.vessel.name)

        print(VesselHelper.get_decouple_stages());

        self.vessel.control.sas = False;
        self.vessel.control.rcs = False;
        self.vessel.control.throttle = low_orbit_throttle;


    def countdown(self):

        # Countdown...
        print('3...'); time.sleep(1)
        print('2...'); time.sleep(1)
        print('1...'); time.sleep(1)
        print('Launch!')

    def engage_autopilot(self):
        self.vessel.control.activate_next_stage();

        self.vessel.auto_pilot.engage();
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90);


    def activate(self,low_orbit_throttle):
        self.preflight_setup(low_orbit_throttle)
        self.countdown()
        self.engage_autopilot()

        #if launchclamps
            #engage engines
            #decouple decouplers

            #decouple decouplers
            #engage engines
            #release launch clamps

    def coastToAltitude(self,target_altitude):
        #power down when approaching target altitude
        self.vessel.control.throttle = 0.25;
        while VesselHelper.apoapsis() < target_altitude:
            pass

        #throttle off
        print("Target altitude reached")
        self.vessel.control.throttle = 0;

        # Wait until out of atmosphere
        print('Coasting out of atmosphere')
        while VesselHelper.altitude() < 70500:
            pass

    def controlLowOrbitThrust(self):
        speed = self.vessel.flight(self.vessel.orbit.body.reference_frame).speed
        if VesselHelper.altitude() < 10000 and speed > 200.:
            self.vessel.control.throttle = 0.5;
        elif speed < 200:
            self.vessel.control.throttle = 1;

    def gravityTurn(self,turn_start_altitude, turn_end_altitude, target_altitude):
        boosters_separated=False;
        turn_angle=0;

        while True:

            self.controlLowOrbitThrust()

            #Gravity Turn
            if VesselHelper.altitude() > turn_start_altitude and VesselHelper.altitude() < turn_end_altitude:
                frac = (VesselHelper.altitude() - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
                new_turn_angle = frac * 90

                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90-turn_angle,90)

          # Separate SRBs when finished
            if not boosters_separated:
                if VesselHelper.liquid_booster_fuel() < 0.1:
                    self.vessel.control.activate_next_stage()
                    boosters_separated = True
                    print('Boosters separated')

            if VesselHelper.apoapsis() > target_altitude*0.9:
                print('Approaching target apoapsis')
                break


        self.coastToAltitude(target_altitude)

