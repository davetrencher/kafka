from kafka.helper.krpchelper import KrpcHelper

class Date:


    DAWN = "dawn"
    NOON = "noon"
    SUNSET = "sunset"

    # based on Kerbin may need to change.
    # sunrise: 4:13ish
    # sunset: 1:09ish
    _DAWN = "4:13:0"
    _NOON = "5:45"
    _SUNSET = "1:13:0"

    DAYS_IN_YEAR = 426
    HOURS_IN_DAY = 6
    MINUTES_IN_HOUR = 60
    SECONDS_IN_MINUTE = 60
    SECONDS_IN_HOUR = MINUTES_IN_HOUR * SECONDS_IN_MINUTE
    SECONDS_IN_DAY = HOURS_IN_DAY * SECONDS_IN_HOUR
    SECONDS_IN_YEAR = DAYS_IN_YEAR * SECONDS_IN_DAY


    # use TimeHelper static variables or "hh:mm"
    @classmethod
    def get_instance_time_of_day(cls,time_of_day):
        date = cls.get_instance_from_ut()
        result = {
            Date.DAWN: Date._DAWN,
            Date.NOON: Date._NOON,
            Date.SUNSET: Date._SUNSET,
        }.get(time_of_day)

        date.__set_time(result)
        return date.as_seconds()

    @classmethod
    def get_instance_from_ut(cls):
        return cls.get_instance_from_seconds(KrpcHelper.ut())

    @classmethod
    def get_instance_from_seconds(cls,seconds):

        year, remainder = divmod(seconds, Date.SECONDS_IN_YEAR)
        days, remainder = divmod(remainder, Date.SECONDS_IN_DAY)
        hours, remainder = divmod(remainder, Date.SECONDS_IN_HOUR)
        mins, secs = divmod(remainder, Date.SECONDS_IN_MINUTE)

        return cls(year, days, hours, mins, secs)

    def __set_time(self, time):
        parts = time.split(":")
        self.hours, self.minutes = int(parts[0]), int(parts[1])

        if len(parts) > 2:
            self.seconds = int(parts[2])
        else:
            self.seconds = 0;

    def __init__(self, year, days, hours, minutes, seconds = 0):
        self.year = int(year)
        self.days = int(days)
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)

    def as_seconds(self):
        year_secs = int(self.year * Date.SECONDS_IN_YEAR)
        day_secs = int(self.days * Date.SECONDS_IN_DAY)
        hour_secs = int(self.hours * Date.SECONDS_IN_HOUR)
        mins_secs = int(self.minutes * Date.SECONDS_IN_MINUTE)

        return year_secs + day_secs + hour_secs + mins_secs + self.seconds

    def to_string(self):
        return "Y{}, D{}, {}:{:02d}:{:02d}".format(self.year+1, self.days+1, self.hours, self.minutes, self.seconds)
