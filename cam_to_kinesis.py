import cv2
import logging as log
import datetime as dt
from time import sleep
import time
import base64 #for bytearray
import json
import os
import boto3
import hashlib
import decimal

client = boto3.client('kinesis')

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)
anterior = 0

while True:
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(30, 30)
		
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        start_time = time.time()
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi = frame[y:y+h, x:x+w]
        imgtime = str(dt.datetime.now().strftime("%y_%m_%d_%H_%M_%S_%f"))
        imgname = "croped_face_"+str(len(faces))+"_"+ imgtime +".jpg"
        cv2.imwrite(imgname ,roi)
        with open(imgname, "rb") as imageFile:
          img_str = imageFile.read()
          b = bytearray(img_str)
          print(type(b))
          img_bytes = base64.b64encode(b)
        print imgname
        my_json_string = {'img': img_bytes, 'time': imgtime }
        os.remove(imgname)
        print "writing in queue now..."
        response = client.put_record(
                        StreamName='<<<YOUR STREM>>>',
                        Data=json.dumps(my_json_string),
                        PartitionKey=str(shopnumber))
        print response
    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))
		
    # Display the resulting frame
    cv2.imshow('Video', frame)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
