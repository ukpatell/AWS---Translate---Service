
import json
import os
import boto3

def lambda_handler(event, context):
    client = boto3.client('stepfunctions')
    
    for record in event['Records']:
        key = record['s3']['object']['key']
        object_name = key.split("/")[-1]
        file_extension = object_name.split(".")[-1]
        state_machine = os.environ['TRANSLATE_DOCUMENT_SFN_ARN']
        print(state_machine)
        if file_extension in ["txt", "TXT", "text", "TEXT"]:
            response = client.start_execution(
              stateMachineArn= state_machine,
              input=json.dumps(event)
            )
