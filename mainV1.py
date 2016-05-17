import httplib2
import os
from activity import Activity
from calender_manager import CalenderManager

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # Type in start day & end day
    start = datetime.datetime(2016, 5, 18, hour=0, minute=0)
    end = datetime.datetime(2016, 5, 22, hour=23, minute=59)

    # Create the time spenders
    colors = service.colors().get().execute()
    # Print available event colors.
    print colors["event"]

    a = Activity("OpenWorm", 6, 10, "1", preferred_day_before=3)
    b = Activity("Reading", 4, 10, "2")

    act = [a, b]

    cm = CalenderManager(act, service, start, end)

    # Get the free time blocks, seperate them by day
    # day_arr = Sort them by day
    # prio_arr = Sort them by priority

    # run()
    cm.run()


'''

    BEGIN ALLOCATION
    current day = monday
    mon = Get all open time blocks in monday
    iterate through timeblocks(
        tryTimeBlockDay(mon, timeblock)
        do
            len = timeblock.length
            for each el in mon
                done, timeblock = el.add(timeblock)
                if(done):  remove el from every subsequent day array and monday
        while(len != timeblock.length && timeblock.length != 0)
        if(timeblock.length > 0)
            return timeblock
    )

    for each day in week
        tb = getTimeBlocks(day)
        day_activities = day_arr[day]
        for each block in tb:
            if day_act not empty:
                timeblock = tryTimeBlockByDay(tb, day_activities)
                if(timeblock.len > 0){
                    timeblock = tryTimeBlockByPrio(tb)
                    if(timeblock.len > 0):
                        print unusable time block
                }
            else:
                timeblock = tryTimeBlockByPrio(tb)
                    if(timeblock.len > 0):
                        print unusable time block



    Go to prio 1 and fill do thing.add(timeblock) round robin, do the same for the rest of the prios
    while there are times blocks still in the list

    Go onto the next day

'''
'''
    thing.add(timeblock)
    if completed
        return true, timeblock
    if mintime < timeblock
'''





if __name__ == '__main__':
    main()