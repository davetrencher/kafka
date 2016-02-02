import time


class LaunchControl:

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

    def preflight_setup(self,low_orbit_throttle):

        self.vessel.control.sas = False;
        self.vessel.control.rcs = False;
        self.vessel.control.throttle = low_orbit_throttle;


    def countdown(self):

        # Countdown...
        print('3...'); time.sleep(1)
        print('2...'); time.sleep(1)
        print('1...'); time.sleep(1)
        print('Launch!')
        self.decorated.stage();

    def engage_autopilot(self):

        self.vessel.auto_pilot.engage();
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90);
        print("Autopilot engaged we have lift off")


    def activate(self,low_orbit_throttle):
        print("Current stage is: ",self.vessel.control.current_stage)
        self.preflight_setup(low_orbit_throttle)
        self.decorated.retract_launchtowers();
        self.countdown()
        self.engage_autopilot()
        self.decorated.disengage_launch_clamps();



    def coastToAltitude(self,target_altitude):
        #power down when approaching target altitude
        self.vessel.control.throttle = 0.25;
        while self.decorated.apoapsis() < target_altitude:
            pass

        #throttle off
        print("Target altitude reached")
        self.vessel.control.throttle = 0;

        # Wait until out of atmosphere
        print('Coasting out of atmosphere')
        while self.decorated.altitude() < 70500:
            pass

    def controlLowOrbitThrust(self):
        speed = self.vessel.flight(self.vessel.orbit.body.reference_frame).speed
        if self.decorated.altitude() < 10000 and speed > 200.:
            self.vessel.control.throttle = 0.5;
        elif speed < 200:
            self.vessel.control.throttle = 1;

    def gravityTurn(self,turn_start_altitude, turn_end_altitude, target_altitude):
        print("gravity turn")
        print(self.decorated.booster_stage())
        boosters_separated=False or self.decorated.booster_stage() == -1;
        print(boosters_separated)
        turn_angle=0;

        while True:

         #   self.controlLowOrbitThrust()
            self.decorated.describe_thrust();

            #Gravity Turn
            if self.decorated.altitude() > turn_start_altitude and self.decorated.altitude() < turn_end_altitude:
                frac = (self.decorated.altitude() - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
                new_turn_angle = frac * 90

                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90-turn_angle,90)

          # Separate SRBs when finished
            if not boosters_separated:
                if self.decorated.booster_fuel() < self.decorated.min_booster_fuel():
                    self.decorated.stage()
                    boosters_separated = True
                    print('Boosters separated thrust is: ', self.vessel.thrust)
                    if (self.vessel.thrust == 0.0):
                        print("no thrust! Probably separate stage and engine lets try again.")
                        self.decorated.stage()

            if self.decorated.apoapsis() > target_altitude*0.9:
                print('Approaching target apoapsis')
                break


        self.coastToAltitude(target_altitude)

