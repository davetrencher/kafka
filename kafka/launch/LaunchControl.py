import time

from kafka.helper.Logger import Logger


class LaunchControl:

    def __init__(self, vessel):
        self.vessel = vessel.vessel
        self.decorated = vessel

    def preflight_setup(self,low_orbit_throttle):

        self.vessel.control.sas = False;
        self.vessel.control.rcs = False;
        self.decorated.set_throttle(low_orbit_throttle);
        self.engage_autopilot()


    def countdown(self):

        print("Countdown sequence initiated")
        print('T Minus 10'); time.sleep(1)
        print('9...'); time.sleep(1)
        print('8...'); time.sleep(1)
        print('7...'); time.sleep(1)
        print('6...'); time.sleep(1)
        print('5...'); time.sleep(1)
        print('4...'); time.sleep(1)
        print('3...'); time.sleep(1)
        print('2...'); time.sleep(1)
        print('1...'); time.sleep(1)
        print('Launch!')
        self.decorated.stage();

    def engage_autopilot(self):

        self.vessel.auto_pilot.engage();
        self.vessel.auto_pilot.target_pitch_and_heading(90, 90);
        Logger.log("Autopilot engaged we have lift off")


    def activate(self,low_orbit_throttle):
        Logger.log("Current stage is: {}".format(self.vessel.control.current_stage))
        self.preflight_setup(low_orbit_throttle)
        self.countdown()

        while self.decorated.twr() < 1.2:
            Logger.log("TWR: {:.2f}".format(self.decorated.twr()))
            time.sleep(0.5)

            if (self.decorated.twr() == 0.0 ):
                Logger.log("No thrust attempt stage - probably needs to check for engine presence on current stage.")
                self.decorated.stage()
            elif (self.decorated.max_stage_twr() < 1.2):
                Logger.log("Max available thrust is < 1.2 activating next stage.")
                self.decorated.stage()
            pass
        self.decorated.disengage_launch_clamps();



    def coastToAltitude(self,target_altitude):
        #power down when approaching target altitude
        self.vessel.control.throttle = 0.25;
        while self.decorated.apoapsis() < target_altitude:
            pass

        #throttle off
        Logger.log("Target altitude reached")
        self.vessel.control.throttle = 0;

        # Wait until out of atmosphere
        Logger.log('Coasting out of atmosphere')
        while self.decorated.altitude() < 70500:
            pass

    def controlLowOrbitThrust(self):
        speed = self.vessel.flight(self.vessel.orbit.body.reference_frame).speed
        if self.decorated.altitude() < 10000 and speed > 200.:
            self.decorated.set_throttle(float(0.5));
        elif speed < 200:
            self.decorated.set_throttle(1);

    def gravityTurn(self,turn_start_altitude, turn_end_altitude, target_altitude):
        Logger.log("Gravity turn")

        turn_angle=0;

        while True:

            self.decorated.log_flight_data();

            #Gravity Turn
            if self.decorated.altitude() > turn_start_altitude and self.decorated.altitude() < turn_end_altitude:
                frac = (self.decorated.altitude() - turn_start_altitude) / (turn_end_altitude - turn_start_altitude)
                new_turn_angle = frac * 90

                if abs(new_turn_angle - turn_angle) > 0.5:
                    turn_angle = new_turn_angle
                    self.vessel.auto_pilot.target_pitch_and_heading(90-turn_angle,90)

          # Separate SRBs when finished
            booster_stage = self.decorated.current_decouple_stage()

            if self.decorated.is_decouple_stage_resources_exhausted(booster_stage):
                self.decorated.stage()
                Logger.log('Boosters separated thrust is: {:.2f}'.format(self.vessel.thrust))
                while (self.vessel.thrust == 0.0):
                    Logger.log("No thrust! Probably separate stage and engine lets try again.")
                    time.sleep(1)
                    self.decorated.stage()

            if self.decorated.apoapsis() > target_altitude*0.9:
                Logger.log('Approaching target apoapsis')
                break


        self.coastToAltitude(target_altitude)

