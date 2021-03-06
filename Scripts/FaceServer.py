import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
import time
import face_recognition
import numpy as np
import uuid
import datetime
import os



cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': "iotfinal-a2cfe",
  'databaseURL': "https://iotfinal-a2cfe.firebaseio.com",
  'storageBucket': "iotfinal-a2cfe.appspot.com"
})

# REMOVE ALL PEOPLE & START OVER.
db.reference('people').delete()

processed_dic = db.reference('people').get()
processed = []
processed_data = []
if processed_dic:
    for key, item in processed_dic.items():
        processed.append(np.array(item['encoding']))
        item['id'] = key
        processed_data.append(item)
else:
    processed_dic = {}



while(1):
    unprocessed = db.reference('unprocessed').get()
    print('Waiting ', str(datetime.datetime.utcnow()))
    if not unprocessed:
        time.sleep(5)
    else:
        for key, item in unprocessed.items():
            print('PROCESSING FACE : ', key)
            db.reference('unprocessed').child(key).delete()
            db.reference('identified').child(key).set(item)
            encoding = np.array(item['encoding'])
            best_match = 2
            if processed:
                bm_index = 0
                for poc_indexm, poc_encoding in enumerate(processed):
                    fc_val = face_recognition.face_distance([poc_encoding], encoding)
                    if fc_val < best_match:
                        bm_index = poc_indexm
                        best_match = fc_val
            if best_match < .56:
                person = processed_data[bm_index]
                person['visits'][key] = item
                person['visits'][key].pop('encoding')
                person['most_recent'] = item['timestamp']
                person_db = db.reference('people').child(processed_data[bm_index]['id']).get()
                db.reference('people').child(processed_data[bm_index]['id']).child('visits').set(person['visits'])
                db.reference('people').child(processed_data[bm_index]['id']).child('most_recent').set(person['most_recent'])
            else:
                id = str(str(uuid.uuid4()))
                info = {}
                info['visits'] = {key: item}
                info['visits'][key].pop('encoding')
                info['name'] = 'unknown'
                info['encoding'] = encoding.tolist()
                info['most_recent'] = item['timestamp']
                db.reference('people').child(id).set(info)
                processed.append(encoding)
                info['encoding'] = encoding
                info['id'] = id
                processed_data.append(info)





