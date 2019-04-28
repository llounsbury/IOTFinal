import cv2
import face_recognition
import uuid
import datetime
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': "iotfinal-a2cfe",
  'databaseURL': "https://iotfinal-a2cfe.firebaseio.com",
  'storageBucket': "iotfinal-a2cfe.appspot.com"
})

bucket = storage.bucket()
camera_id = '2'


def getFrame():
  cap = cv2.VideoCapture('http://localhost:8090/camera.mjpeg')
  ret, frame = cap.read()
  cap.release
  return frame


while True:
  frame = getFrame()
  small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)
  rgb_small_frame = small_frame[:, :, ::-1]
  face_locations = face_recognition.face_locations(rgb_small_frame)
  for index, location in enumerate(face_locations):
      A = int(location[0] * 1)
      B = int(location[1] * 1)
      C = int(location[2] * 1)
      D = int(location[3] * 1)
      face_locations[index] = (A,B,C,D)
  face_encodings = face_recognition.face_encodings(frame, face_locations)
  for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
    print('FOUND FACE')
    id = str(uuid.uuid4())
    visit = {'timestamp': str(datetime.datetime.utcnow()), 'encoding': encoding.tolist(), 'camera': camera_id}
    #cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
    face = frame[top:bottom, left:right]
    face = cv2.resize(face, (250, 250))
    #cv2.imshow('FACE', face)
    cv2.imwrite(id+'.jpg', face)
    blob = bucket.blob(id + '.jpg')
    with open(id+'.jpg', 'rb') as face_image:
      blob.upload_from_file(face_image, content_type='image/jpg')
    #os.remove(id+'.jpg')
    db.reference('unprocessed').child(id).set(visit)
  #cv2.imshow('Video', frame)





  if cv2.waitKey(1) == 27:
    exit(0)