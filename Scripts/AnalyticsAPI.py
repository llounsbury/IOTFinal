from flask import Flask
from flask import jsonify
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
import datetime
import json
from datetime import datetime as dt
from datetime import date, timedelta
from operator import itemgetter
from flask_cors import CORS
import numpy as np
import math
from cmath import rect, phase
from sklearn.cluster import KMeans
import calendar


app = Flask(__name__)
CORS(app)

cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "iotfinal-a2cfe",
    'databaseURL': "https://iotfinal-a2cfe.firebaseio.com",
    'storageBucket': "iotfinal-a2cfe.appspot.com"
})


def activity_spans(uuid):
    # Get a dictionary of all instances of finding a user
    # {image: camera id, timestamp: year-month-day hour:minute:second
    ref = db.reference('people/' + uuid + '/visits').get()
    sighting_times = []
    for sighting in ref.keys():
        sighting_times.append(dt.strptime(ref[sighting]['timestamp'], '%Y-%m-%d %H:%M:%S'))

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


def get_correlated_users(uuid):
    """This function returns a list of users (size of num_results) that are most likely to be seen with the given user."""
    ref = db.reference('people/' + uuid + '/visits').get()
    uuid_list = db.reference('people/').get()
    score = {}
    for uuid_person in uuid_list:
        match = 0
        if uuid != uuid_person:
            score[uuid_person] = 0
            ref2 = uuid_list[uuid_person]['visits']
            for visit in ref2:
                visit_time = dt.strptime(ref2[visit]['timestamp'], '%Y-%m-%d %H:%M:%S')
                for persons_visits in ref:
                    person_visit_time = dt.strptime(ref[persons_visits]['timestamp'], '%Y-%m-%d %H:%M:%S')
                    diff = abs(visit_time - person_visit_time)
                    if diff.seconds == 0:
                        diff.seconds = .25
                    if diff.seconds < 180:
                        score[uuid_person] += 1/(diff.seconds)
    score_list = []
    for key, value in sorted(score.items(), key=lambda item: item[1]):
        score_list.append({key: str(value)[:6]})
    score_list.reverse()
    return score_list[:10]


def mean_angle(deg):
    return math.degrees(phase(sum(rect(1, math.radians(d)) for d in deg)/len(deg)))


def mean_time(times):
    seconds = ((time.second + time.minute * 60 + time.hour * 3600)
               for time in times)
    day = 24 * 60 * 60
    to_angles = [s * 360. / day for s in seconds]
    mean_as_angle = mean_angle(to_angles)
    mean_seconds = mean_as_angle * day / 360.
    if mean_seconds < 0:
        mean_seconds += day
    h, m = divmod(mean_seconds, 3600)
    m, s = divmod(m, 60)
    return '%02i:%02i:%02i' % (h, m, s)


def datetime_to_radians(dt_obj):
    """Calculate radians using 24-hour circle, starting north and moving clockwise"""
    time_of_day = dt_obj.time()
    seconds_from_midnight = 3600 * time_of_day.hour + \
        60 * time_of_day.minute + time_of_day.second
    radians = float(seconds_from_midnight) / float(12 * 60 * 60 * 2 * math.pi)
    return radians

def get_clustered_sighting_times(uuid, num_clusters=5):
    """ This function returns the next expected sighting time (string formatted as HH:MM:SS) of a user at a given camera."""
    ref = db.reference('people/' + uuid + '/visits').get()
    times_to_avg = []
    for key in ref:
        times_to_avg.append(dt.strptime(
            ref[key]['timestamp'], '%Y-%m-%d %H:%M:%S'))
    angles = np.asarray([datetime_to_radians(y) for y in times_to_avg])
    km = KMeans(n_clusters=num_clusters)
    clusters = km.fit_predict(angles.reshape(-1, 1))
    time_clusters = []
    for i in range(num_clusters):
        temp_times_to_avg = []
        for j in range(len(times_to_avg)):
            if(i == clusters[j]):
                temp_times_to_avg.append(times_to_avg[j])
        time_clusters.append(mean_time(temp_times_to_avg))
    return time_clusters


@app.route('/<uuid>')
def getAllAnalytics(uuid):
    allAnaylytics = {}
    try:
        allAnaylytics['visits'] = activity_spans(uuid)
    except:
        print('error 1')
    try:
        allAnaylytics['cameras'] = camera_order_frequency(uuid)
    except:
        print('error 2')
    try:
        allAnaylytics['correlated_users'] = get_correlated_users(uuid)
    except:
        print('error 3')
    try:
        allAnaylytics['cluster'] = get_clustered_sighting_times(uuid)
    except:
        print('error 4')
    return jsonify(allAnaylytics)
