import datetime
import random

class CalenderManager:
    def __init__(self, activities, service, start, end):
        self.activities = activities
        self.service = service
        self.calender_list = self.service.calendarList().list().execute()["items"]

        self.start = start
        self.end = end

        self.mycal_id = self.__get_cal_id("MyCal")
        self.__clear_calender("MyCal")

        self.startstr = start.isoformat() + 'Z'
        self.endstr = end.isoformat() + 'Z'
        self.events, self.sorted_events = self.__get_events(self.startstr, self.endstr)

        self.start_day_of_week = self.start.weekday()

        self.prio_list = self.__sort_by_prio()
        self.day_activities = self.__sort_by_day()
        self.start_day = datetime.timedelta(hours=10)
        self.end_day = datetime.timedelta(hours=23)
        self.free_blocks = self.__get_free_timeblocks()
        self.current_prio = 1

        for a in activities:
            a.set_calender(self.mycal_id)

    def __clear_calender(self, name):
        id = self.__get_cal_id(name)
        events = self.service.events().list(
            calendarId=id).execute()["items"]

        for e in events:
            print "deleting", e["summary"]
            self.service.events().delete(calendarId=id, eventId=e["id"]).execute()

    def __get_cal(self, name):
        for cal in self.calender_list:
            if(cal["summary"] == name):
                return cal

    def __get_cal_id(self, name):
        for cal in self.calender_list:
            if(cal["summary"] == name):
                return cal["id"]

    def __get_events(self, start, end):
        sorted_events = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        events = []
        # print start, end
        for cal in self.calender_list:
            if(cal["summary"] != "Reminders"):
                id = cal["id"]
                # print "start", start
                eventsResult = self.service.events().list(
                    calendarId=id, timeMin=start, singleEvents=True, timeMax=end,
                    orderBy='startTime').execute()["items"]
                events.extend(eventsResult)
                for event in eventsResult:
                    start_temp = event['start']['dateTime']
                    end_temp = event['end']['dateTime']
                    # print start_temp
                    start_temp = start_temp[:-6]
                    end_temp = end_temp[:-6]
                    start_temp = datetime.datetime.strptime(start_temp, "%Y-%m-%dT%H:%M:%S")
                    end_temp = datetime.datetime.strptime(end_temp, "%Y-%m-%dT%H:%M:%S")
                    dows = start_temp.weekday()
                    if(start_temp > self.start):
                        sorted_events[dows].append(Interval(start_temp, end_temp))

        for i in range(0, 7):
            l = sorted_events[i]
            sorted_events[i] = sorted(l, key=lambda ev: ev.start)

        return events, sorted_events

    def __sort_by_prio(self):
        l = {}
        self.max_prio = 0
        for a in self.activities:
            if(a.priority > self.max_prio):
                self.max_prio = a.priority
            if a.priority in l:
                l[a.priority].append(a)
            else:
                l[a.priority] = []
                l[a.priority].append(a)

        # for i in l:
        #     a = l[i]
        #     random.shuffle(a)

        return l

    def __sort_by_day(self):
        l = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        for a in self.activities:
            num = a.preferred_day_before
            if num is not 6:
                for i in range(0, num):
                    l[i].append(a)

        # print l
        return l

    def __get_free_timeblocks(self):
        l = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
        total_time = datetime.timedelta(hours=0)
        count = 0
        for i in range(self.start_day_of_week, 7):
            dt = datetime.timedelta(days=count)
            d1 = self.start + dt + self.start_day
            d2 = self.start + dt + self.end_day
            print "d", d1, d2
            inte = Interval(d1, d2)
            events = self.sorted_events[i]
            print events
            my_interval = inte
            for ev in events:
                print "event", ev
                print "interval", my_interval
                first, last = my_interval.split(ev)
                print "fl", first, last
                if first is not None:
                    l[i].append(first)
                    total_time += (first.end - first.start)
                my_interval = last
                if(my_interval is None):
                    break
                print "****"

            print "-------"

            if my_interval is not None:
                l[i].append(my_interval)
                total_time += (my_interval.end - my_interval.start)

            count += 1

        for a in self.activities:
            a.set_total_amount_of_time(total_time)

        return l

    def run(self):
        zero = datetime.timedelta(seconds=0)
        for i in range(self.start_day_of_week, 7):
            timeblocks = self.free_blocks[i]
            print timeblocks
            day_activities = self.day_activities[i]
            for block in timeblocks:
                if len(day_activities) != 0:
                    block = self.test_interval_day(block, day_activities, i)
                    # return
                    if(block.length() > zero):
                        finished, block = self.test_interval_prio(block)
                        if(block.length() > zero):
                            print block, "Unusable time block"
                        if(finished):
                            return

                else:
                    finished, block = self.test_interval_prio(block)
                    if(block.length() > zero):
                        print block, "unusable time block"
                    if(finished):
                            return

    def test_interval_day(self, interval, activites, day):
        mylen = interval.length()
        zero = datetime.timedelta(seconds=0)
        for el in activites:
            done, interval = el.add(interval, self.service)
            if(done):
                activites.remove(el)
                for i in range(day, el.preferred_day_before):
                    if el in self.day_activities[i]:
                        self.day_activities[i].remove(el)

        while(mylen != interval.length() and interval.length() != zero):
            mylen = interval.length()
            for el in activites:
                done, interval = el.add(interval, self.service)
                if(done):
                    activites.remove(el)
                    for i in range(day, el.preferred_day_before):
                        if el in self.day_activities[i]:
                            self.day_activities[i].remove(el)

        return interval

    def get_current_priority(self):
        if(len(self.prio_list[self.current_prio]) == 0):
            self.current_prio += 1

        if (self.current_prio > self.max_prio):
            return []

        return self.prio_list[self.current_prio]


    def test_interval_prio(self, interval):
        zero = datetime.timedelta(seconds=0)
        activities = self.get_current_priority()
        if(len(activities) == 0):
            return True, interval

        mylen = interval.length()
        for el in activities:
            done, interval = el.add(interval, self.service)
            if(done):
                activities.remove(el)
                if el in self.prio_list[self.current_prio]:
                    self.prio_list[self.current_prio].remove(el)
                if(len(activities) == 0):
                    activites = self.get_current_priority()
                    if(len(activities) == 0):
                        return True, interval

        while(mylen != interval.length() and interval.length() != zero):
            mylen = interval.length()
            for el in activities:
                done, interval = el.add(interval, self.service)
                if(done):
                    activites.remove(el)
                    if el in self.prio_list[self.current_prio]:
                        self.prio_list[self.current_prio].remove(el)
                    if(len(activities) == 0):
                        activites = self.get_current_priority()
                        if(len(activities) == 0):
                            return True, interval

        return False, interval



class Interval:
    def __init__(self, start, end):
        # These are datetimes
        self.start = start
        self.end = end

    def __repr__(self):
        return str(self.start) + "  /  " + str(self.end)

    def length(self):
        return self.end - self.start

    def split(self, event):
        c1 = None
        c2 = None
        if(event.end < self.start and event.start < self.start):
            # print 1
            c2 = self
            return c1, c2
        elif(event.start < self.start):
            # print 2
            c2 = Interval(event.end, self.end)
            return c1, c2

        dt = datetime.timedelta(minutes=30)
        if (event.start - self.start) > dt:
            # print 3
            c1 = Interval(self.start, event.start)
        if (self.end - event.end) > dt:
            # print 4
            c2 = Interval(event.end, self.end)

        return c1, c2