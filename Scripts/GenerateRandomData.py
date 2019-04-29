import cv2
import face_recognition
import uuid
import datetime
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from random import randint


# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "iotfinal-a2cfe",
    'databaseURL': "https://iotfinal-a2cfe.firebaseio.com",
    'storageBucket': "iotfinal-a2cfe.appspot.com"
})

Images = '/Users/llounsbury/Desktop/RandomFaces/'
images = os.listdir(Images)
images.remove('.DS_Store')


bucket = storage.bucket()
start_date = datetime.datetime.strptime("2019-04-15 21:13:09", '%Y-%m-%d %H:%M:%S')
stop_date = datetime.datetime.strptime("2019-04-20 21:13:09", '%Y-%m-%d %H:%M:%S')

while (start_date < stop_date):
    camera_id = randint(1, 2)
    interval = randint(1,3)
    if interval == 1:
        start_date = start_date + datetime.timedelta(seconds=600)
    elif interval == 2:
        start_date = start_date + datetime.timedelta(seconds=3)
    elif interval == 3:
        start_date = start_date + datetime.timedelta(seconds=3600)
    rand_image = images[randint(0, len(images) - 1)]
    print(rand_image)
    frame = cv2.imread(Images + rand_image)
    face_locations = face_recognition.face_locations(frame)
    for index, location in enumerate(face_locations):
        A = int(location[0] * 1)
        B = int(location[1] * 1)
        C = int(location[2] * 1)
        D = int(location[3] * 1)
        face_locations[index] = (A, B, C, D)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
        print('FOUND FACE')
        id = str(uuid.uuid4())
        visit = {'timestamp': str(start_date), 'encoding': encoding.tolist(), 'camera': camera_id}
        # cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        face = frame[top:bottom, left:right]
        face = cv2.resize(face, (250, 250))
        # cv2.imshow('FACE', face)
        cv2.imwrite(id + '.jpg', face)
        blob = bucket.blob(id + '.jpg')
        with open(id + '.jpg', 'rb') as face_image:
            blob.upload_from_file(face_image, content_type='image/jpg')
        os.remove(id+'.jpg')
        db.reference('unprocessed').child(id).set(visit)
    # cv2.imshow('Video', frame)

    if cv2.waitKey(1) == 27:
        exit(0)
