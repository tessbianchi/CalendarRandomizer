import datetime
from calender_manager import Interval

class Activity:
    def __init__(self, name, percent_num, percent_den, color_id, preferred_day_before=6, priority=1):
        self.name = name
        self.percent_num = percent_num
        self.percent_den = percent_den
        self.preferred_day_before = preferred_day_before
        self.color_id = color_id
        self.priority = priority

    def create_event(self, start_time, end_time):
        print "creating event", self.name, start_time, end_time
        event = {
            'summary': self.name,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/New_York',
            },
            'colorId': self.color_id
        }
        event = self.service.events().insert(calendarId=self.cal_id, body=event).execute()

    def add(self, timeblock, service):
        self.service = service
        print "adding"
        print timeblock
        print self.time_left
        zero = datetime.timedelta(seconds=0)
        hour = datetime.timedelta(hours=1)
        if(timeblock.length() == zero):
            print 0
            return False, timeblock
        if(self.time_left == zero):
            print 1
            return True, timeblock

        # see the length of the time block
        ltb = timeblock.length()

        # ltb > time_left, add it and return the remainder of the timeblock
        if(ltb > self.time_left):
            print 2
            self.create_event(timeblock.start, timeblock.start + self.time_left)
            timeblock = Interval(timeblock.start + self.time_left, timeblock.end)
            self.time_left = zero
            print "PROB"
            print timeblock
            return True, timeblock

        else:
            a = self.time_left - ltb
            if(a > hour):
                print 3
                self.create_event(timeblock.start, timeblock.end)
                self.time_left = a
                timeblock = Interval(timeblock.start, timeblock.start)
                return False, timeblock

        return False, timeblock

    def set_total_amount_of_time(self, dt):
        self.total_time = dt
        self.time = self.total_time * self.percent_num / self.percent_den
        self.time_left = self.time

    def set_calender(self, cal_id):
        self.cal_id = cal_id



