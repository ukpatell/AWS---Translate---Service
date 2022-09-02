import json
import boto3

client = boto3.client('translate')

def lambda_handler(event, context):
    print('Request Recieved: ',event)

    response = client.translate_text(
        Text= event['text'],
        SourceLanguageCode=event['source'],
        TargetLanguageCode=event['target'],
    )
    data = response['TranslatedText']
    print('Response Recieved: ',data)
    return data
