from kafka.helper.krpchelper import KrpcHelper

import math


class DateHelper:

    YEAR = "year"
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"

    DAWN = "dawn"
    NOON = "noon"
    SUNSET = "sunset"

    #based on Kerbin may need to change.
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

    @staticmethod
    def convert_date_time_to_seconds(year,day,hours,minutes,seconds = 0):

        year_secs = float(year) * DateHelper.SECONDS_IN_YEAR
        day_secs = float(day) * DateHelper.SECONDS_IN_DAY
        hour_secs = float(hours) * DateHelper.SECONDS_IN_HOUR
        mins_secs = float(minutes) * DateHelper.SECONDS_IN_MINUTE

        return float(year_secs) + float(day_secs) + float(hour_secs) + float(mins_secs) + float(seconds)

    @staticmethod
    def convert_date_to_seconds(date):
        return DateHelper.convert_date_time_to_seconds(date.year, date.days, date.hours, date.minutes, date.seconds)

    @staticmethod
    def convert_ut_to_date():

        return DateHelper.convert_seconds_to_date(KrpcHelper.ut())


    @staticmethod
    def convert_seconds_to_date(seconds):
        years = seconds / DateHelper.SECONDS_IN_YEAR
        remainder, year = math.modf(years)
        remainder, days = math.modf(remainder * DateHelper.DAYS_IN_YEAR)
        remainder, hours = math.modf(remainder * DateHelper.HOURS_IN_DAY)
        secs, mins = math.modf(remainder * DateHelper.MINUTES_IN_HOUR)
        remainder, secs = math.modf(remainder * DateHelper.SECONDS_IN_MINUTE)

        return Date(year, days, hours, mins, secs)

    @staticmethod
    def set_time(date,time):
        parts = time.split(":")
        date.hours, date.minutes = parts[0],parts[1]

        if len(parts) > 2:
            date.seconds = parts[2]
        else:
            date.seconds = 0;

        return date

    #use TimeHelper static variables or "hh:mm"
    @staticmethod
    def get_ut_at_time_of_day(time_of_day):
        date = DateHelper.convert_ut_to_date()
        result = {
            DateHelper.DAWN : DateHelper._DAWN,
            DateHelper.NOON : DateHelper._NOON,
            DateHelper.SUNSET : DateHelper._SUNSET,
        }.get(time_of_day)

        return DateHelper.set_time(date, result).as_seconds()

class Date:

    def __init__(self, year, days, hours, minutes, seconds = 0):
        self.year = int(year)
        self.days = int(days)
        self.hours = int(hours)
        self.minutes = int(minutes)
        self.seconds = int(seconds)

    def as_seconds(self):
        return DateHelper.convert_date_to_seconds(self)

    def to_string(self):
        return "Y{}, D{}, {}:{:02d}:{:02d}".format(self.year, self.days, self.hours, self.minutes, self.seconds)
