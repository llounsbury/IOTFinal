"""
user_analytics.py
Description: Analytics module for ECE:5550 IoT final project
"""

'''
TODO: SOME NOTES I TOOK. DELETE LATER.

Analytics ideas:
- When does a user show up at a camera location?
  - Arguments: uuid, camera
  - Returns: timestamp (when the user is most likely to show up at a certain camera)
  - Implementation: Average times user is seen at camera, possibly excluding outliers.
- How long does someone spend at the store? (one at entrance, one at exit)
  - Arguments: uuid, entry camera, exit camera
  - Returns: length of time
  - Implementation: Calculate difference in time between user sighting at entry and exit.
- Anticipated path
  - Arguments: uuid, camera
  - Returns: camera (at which user is most likely to been seen next), confidence?
  - Implementation: Based on given camera, find shortest average amount of time to next camera sighting of user.
- Correlation between users
  - Arguments: uuid, number of results desired
  - Returns: uuid(s) (users most likely to be seen with given user)
  - Implementation: Calculate shortest amount of time between user sightings at all cameras. Users seen more closely together (in terms of time) are more closely correlated.
- Busiest camera times?
'''

import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
import datetime
import json
from datetime import datetime as dt
from datetime import date, timedelta
from operator import itemgetter


cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': "iotfinal-a2cfe",
  'databaseURL': "https://iotfinal-a2cfe.firebaseio.com",
  'storageBucket': "iotfinal-a2cfe.appspot.com"
})


def get_expected_sighting_time(uuid, camera):
    # This function returns the next expected sighting time (string formatted as HH:MM:SS) of a user at a given camera.
    # TODO? Figure out more efficient way to query DB?
    ref = db.reference('people/' + uuid + '/visits').get()
    times_to_avg = []
    for key in ref:
        print(key) # For testing
        print(ref[key]['camera'])
        if ref[key]['camera'] == camera:
            times_to_avg.append(dt.strptime(ref[key]['timestamp'], '%Y-%m-%d %H:%M:%S')) # Strips fractional seconds
    avg = 0
    # TODO? Come up with more efficient alg for finding time using panda?
    for time in times_to_avg:
        avg += time.second + 60*time.minute + 3600*time.hour
    if len(times_to_avg) != 0:
        avg = avg / len(times_to_avg)
        return str(int(avg/3600)).zfill(2) + ':' + str(int((avg%3600)/60)).zfill(2) + ':' + str(int(avg%60)).zfill(2)
    else:
        return None


# This function looks at one user, and find the time span in which they were seen each day
# Loop through their sightings, for each day keep track of their first and last sighting
# This will provide primarily utility for further analytics
def get_active_times(uuid):
    # Get a dictionary of all instances of finding a user
    # {image: camera id, timestamp: year-month-day hour:minute:second
    ref = db.reference('people/' + uuid + '/visits').get()

    # Build a dictionary structured as follows: {date: {'first': first sighting, 'last': last sighting}}
    daily_data = {}
    for sighting in ref.keys():
        current = dt.strptime(ref[sighting]['timestamp'], '%Y-%m-%d %H:%M:%S')
        daily_data.setdefault(current.date(), {'first': current.time(), 'last': current.time()})

        if daily_data[current.date()]['first'] > current.time():
            daily_data[current.date()]['first'] = current.time()

        if daily_data[current.date()]['last'] < current.time():
            daily_data[current.date()]['last'] = current.time()

    # Return daily data
    return daily_data


# This will return the average active time for a user in any given day
def average_daily_activity_span(uuid):
    daily_data = get_active_times(uuid)
    day_spans = []

    # Calculate the timedelta between first and last sightings each day
    for day in daily_data:
        day_spans.append(dt.combine(date.min, daily_data[day]['last']) - dt.combine(date.min, daily_data[day]['first']))

    # Return the average timedelta for all days
    return sum(day_spans, datetime.timedelta(0)) / len(day_spans)


# This will return the average active time for a user overall within an activity period of 30 mins
def activity_spans(uuid):
    # Get a dictionary of all instances of finding a user
    # {image: camera id, timestamp: year-month-day hour:minute:second
    ref = db.reference('people/' + uuid + '/visits').get()
    sighting_times = []
    for sighting in ref.keys():
        sighting_times.append(dt.strptime(ref[sighting]['timestamp'][:-7], '%Y-%m-%d %H:%M:%S'))

    sighting_times = sorted(sighting_times)
    encounters = {}
    encounter_id = 1
    for current in sighting_times:
        encounters.setdefault(encounter_id, {'first': current, 'last': current})

        if current - encounters[encounter_id]['last'] < datetime.timedelta(minutes=30):
            encounters[encounter_id]['last'] = current
        else:
            encounter_id += 1
            encounters.setdefault(encounter_id, {'first': current, 'last': current})
    output = []
    # Convert for compatibility
    for id in encounters.keys():
        output.append({'start': str(encounters[id]['first']), 'end': str(encounters[id]['last'])})
    return output


def camera_order_frequency(uuid):
    # Get a dictionary of all instances of finding a user
    # {image: camera id, timestamp: year-month-day hour:minute:second
    ref = db.reference('people/' + uuid + '/visits').get()
    sighting_times = []
    for sighting in ref.keys():
        sighting_times.append([dt.strptime(ref[sighting]['timestamp'], '%Y-%m-%d %H:%M:%S'), ref[sighting]['camera']])

    sighting_times.sort(key=itemgetter(0))

    camera_distribution = {}
    order = []
    last_camera = None
    prev_sighting = None
    for sighting in sighting_times:

        if prev_sighting is None or sighting[0] - prev_sighting[0] < datetime.timedelta(minutes=30):
            if not sighting[1] == last_camera:
                last_camera = sighting[1]
                order.append(last_camera)
                prev_sighting = sighting
        else:
            camera_distribution.setdefault(str(order), 0)
            camera_distribution[str(order)] += 1
            order = []
            last_camera = None
            prev_sighting = None
    return camera_distribution


def get_time_between_cameras(uuid, camera1, camera2):
    """This function returns the average amount of time between user sightings at two cameras."""
    pass


def get_expected_next_camera(uuid, camera):
    """This function returns the next camera the user is expected to be sighted at given a particular camera."""
    pass


def get_correlated_users(uuid, num_results):
    # This function returns a list of users (size of num_results) that are most likely to be seen with the given user.
    pass


# Call functions for a quick and dirty test.

