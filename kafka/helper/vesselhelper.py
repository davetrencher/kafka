from kafka.helper.krpchelper import KrpcHelper

class VesselHelper:

    conn = KrpcHelper.conn

    vessel = conn.space_center.active_vessel

    altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
    main_body_resources = vessel.resources_in_decouple_stage(stage=4, cumulative=False)
    liquid_booster_resources = vessel.resources_in_decouple_stage(stage=5, cumulative=False)
    liquid_booster_fuel = conn.add_stream(liquid_booster_resources.amount, 'LiquidFuel')

    apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')

    all_parts = vessel.parts.all

    @staticmethod
    def get_decouple_stages():
        print("decouple")
        decoupleStages = set()
        for el in VesselHelper.all_parts:
            decoupleStages.add(el.decouple_stage)

        return sorted(decoupleStages)

    @staticmethod
    def get_launch_clamps():
        print("get launch clamps not yet implemented")

    @staticmethod
    def get_decouple_stages_on_rocket():
        print("get launch clamps not yet implemented")
