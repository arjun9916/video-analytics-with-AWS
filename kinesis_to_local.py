import boto3
import json
from datetime import datetime
import time
import base64


my_stream_name = 'detect_faces'

kinesis_client = boto3.client('kinesis')
rekognition_client = boto3.client('rekognition')

my_shard_id = 'shardId-000000000000'

shard_iterator = kinesis_client.get_shard_iterator(StreamName=my_stream_name,
                                                      ShardId=my_shard_id,
                                                      ShardIteratorType='LATEST')

my_shard_iterator = shard_iterator['ShardIterator']

record_response = kinesis_client.get_records(ShardIterator=my_shard_iterator,
                                              Limit=1)

while 'NextShardIterator' in record_response:
    record_response = kinesis_client.get_records(ShardIterator=record_response['NextShardIterator'], Limit=1)
    #print("Received event: " + json.dumps(event, indent=2))
    #print record_response
    for record in record_response['Records']:
        # Kinesis data is base64 encoded so decode here
        payload = record['Data']
        payload_img = json.loads(payload)
        compare_img = payload_img['img']
        #print compare_img
        #payload = base64.b64decode(record['Data']['img'])
        #payload_img = json.loads(payload)
        #compare_img = payload['img']
        decoded_compare_img = base64.b64decode(compare_img)
        #client = boto3.client('rekognition')
        rekognition = rekognition_client.search_faces_by_image(CollectionId = 'mycollection', Image ={ 'Bytes': decoded_compare_img})
        print (rekognition)
        #print("Decoded payload: " + payload)
    print 'Successfully processed {} records.'.format(len(record_response['Records']))

    #print record_response

    # wait for 5 seconds
    time.sleep(1)