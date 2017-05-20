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
shopnumber = 9999
#PartitionKey = hashlib.md5(shopnumber.encode("utf")).hexdigest()

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
        my_json_string = {'shop_number': shopnumber, 'img': img_bytes, 'time': imgtime }
        #print my_json_string[0]['shop_number']
        #print my_json_string
        os.remove(imgname)
        print "writing in queue now..."
        response = client.put_record(
                        StreamName='detect_faces',
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
'''
        ############SQS send message...######
        #response = client.send_message(
        #QueueUrl='https://sqs.us-east-1.amazonaws.com/128230620959/first_capture',
        #MessageBody= my_json_string
        #)

		###
        response = client.put_record(
          StreamName='aws_face_rek',
          Data= json.dumps(my_json_string),
          PartitionKey= str(shopnumber),
          #ExplicitHashKey='string',
          #SequenceNumberForOrdering='string'
        )
        print response
        resp_status = response['ResponseMetadata']['HTTPStatusCode']
        if resp_status == 200:
         print "Done, the HTTPStatusCode is "+ str(resp_status) +"!!!"
         #os.remove("data_"+ imgtime +".json")
         print (str(dt.datetime.now()) + " seconds " + str((time.time() - start_time)))
        else:
         print "Issue while sending the message!!"
         print "The HTTPStatusCode is " +resp_status
        ShardId_str = ''
        response = client.describe_stream(
          StreamName='aws_face_rek',
          Limit=123,
          #ExclusiveStartShardId='string'
        )
        print response
        response = client.get_shard_iterator(
            StreamName='aws_face_rek',
            ShardId='shardId-000000000000',
            ShardIteratorType='LATEST'
        )
        ShardIterator_str = response['ShardIterator']
        response = client.get_records(
            ShardIterator= ShardIterator_str,
            Limit=123
        )
'''
