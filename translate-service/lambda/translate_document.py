import boto3
from botocore.exceptions import ClientError
from urllib.parse import unquote_plus
import os
import sys



BUCKET_NAME = os.environ['BATCH_BUCKET']
SOURCE_LANGUAGE = ""
TARGET_LANGUAGE = ""
KEY = ""
METADATA = ""

s3client = boto3.client('s3')
s3 = boto3.resource('s3')
translate = boto3.client('translate')

def translate_text(input_text):
    try:
        return translate.translate_text(
            Text=input_text,
            SourceLanguageCode = SOURCE_LANGUAGE,
            TargetLanguageCode = TARGET_LANGUAGE
        )
    except ClientError as e:
        print(e)
        print(f"Ran into exception while translating [{input_text}]")
        print(f"length [{len(input_text)}]")
        print(e)
        if e.response['Error']['Code'] == "ThrottlingException":
            print(f"Translate Service throttled the request")
            return None
        else:
            raise e
    
def lambda_handler(event, context):
    print(event)
    global SOURCE_LANGUAGE,TARGET_LANGUAGE, METADATA

    # Attempts to search the meta-data
    try:
        KEY = unquote_plus(event[0]['s3']['object']['key'], encoding='utf-8')
        METADATA = s3client.head_object(Bucket=BUCKET_NAME, Key=KEY)
        SOURCE_LANGUAGE = METADATA["Metadata"]["source"]
        TARGET_LANGUAGE = METADATA["Metadata"]["target"]
    except ClientError as e:
        raise e
    
    # Unique ID (We're using eTag istead of executionId)
    execution_id = unquote_plus(event[0]['s3']['object']['eTag'], encoding='utf-8')
    print(f"E-TAG for {KEY} IS {execution_id}")

    for record in event:
        print(record)
        object_name = KEY.split("/")[-1]
        upload_key =  "output/" + object_name
        read_path = '/tmp/' + object_name
        write_path = '/tmp/translated-' + object_name
        record['line'] = int(0)
        record['sentence'] = int(0)
        
        try:
            s3.Bucket(BUCKET_NAME).download_file("temp/" + execution_id, write_path)
            line = record['line']
            sen = int(record['sentence'])
            print(f"Record NOW: {record}")
            new_file = open(write_path, "a+")
        except ClientError as e:
            print("No previous progress for this file. Must be the first run.")
            new_file = open(write_path, "w+")
            line = 0
            sen = 0

        # downloading the file to be translated
        s3.Bucket(BUCKET_NAME).download_file(KEY, read_path)

        with open(read_path, "r") as text_file:
            # reading all the content in one step
            all_content = text_file.read() 
            # splitting the content in paragraphs and storing it in an array
            content_array = all_content.split("\n")

        # translating the text using Amazon Translate
        for i in range(line, len(content_array)):
            if content_array[i] != "":
                if sys.getsizeof(content_array[i]) > 5000:
                    # Try to split by sentences
                    print(f"Line {i} is longer than 5000 bytes, splitting it by sentence.")
                    sentences = content_array[i].split(".")
                    
                    for j in range(0, len(sentences)):
                        if sys.getsizeof(sentences[j]) > 5000:
                            print(f"Sentence {j} longer than 5000 bytes. Translate service is unable to process this sentence. Appending original sentence to the result")
                            print(f"Sentence starting with: '{sentences[j]}...'")
                            result = sentences[j]
                        else:
                            if sentences[j] != "":
                                result = translate_text(sentences[j])
                            else:
                                new_file.write("\n")

                        # Stop Lambda and return to step function
                        if result is None:
                            print(f"Translated {i} out of {len(content_array)} lines")
                            print(f"Translated {j} out of {len(sentences)} sentences")
                            new_file.close()
                            s3.Bucket(BUCKET_NAME).upload_file(write_path, "temp/" + execution_id)
                            record['line'] = int(i)
                            record['sentence'] = int(j)
                            record['progress'] = int(round(i / len(content_array) * 100, 2))
                            record['status'] = 'FAILED'
                            print(event)
                            return event

                        if "TranslatedText" in result:
                            new_file.write(result["TranslatedText"])
                        else:
                            new_file.write(result)
                        new_file.write(".")
                else:
                    result = translate_text(content_array[i])

                    # Stop Lambda and return to step function
                    if result is None:
                        print(f"Translated {i} out of {len(content_array)} lines")
                        new_file.close()
                        s3.Bucket(BUCKET_NAME).upload_file(write_path, "temp/" + execution_id)
                        record['line'] = int(i)
                        record['sentence'] = int(0)
                        record['progress'] = int(round(i / len(content_array) * 100, 2))
                        record['status']="FAILED"
                        print(event)
                        return event

                # writing the translated text to local document
                new_file.write(result["TranslatedText"])
                new_file.write("\n")
                record['line'] = int(i)
            else:
                new_file.write("\n")
                record['line'] = int(i)
            
            # Stop processing function when there is less than 30 secs execution time left
            if context.get_remaining_time_in_millis() < 30000:
                print("Less than 30 secs execution timeout left. Shutting down to prevent function timeout")
                print(context.get_remaining_time_in_millis)
                new_file.close()
                s3.Bucket(BUCKET_NAME).upload_file(write_path, "temp/" + execution_id)
                print(f"Translated {i} out of {len(content_array)} lines")
                record['line'] = int(i)
                record['sentence'] = int(j)
                record['progress'] = int(round(i / len(content_array) * 100, 2))
                record['status'] = int(i)
                return event

        new_file.close()

        # writing the translated document to S3
        s3.Bucket(BUCKET_NAME).upload_file(write_path, upload_key,ExtraArgs={"Metadata":{"target":TARGET_LANGUAGE}})
        # Copy doc to processed folder then delete
        s3.Object(BUCKET_NAME, "processed/" + object_name).copy_from(CopySource=BUCKET_NAME + "/" + KEY)
        s3.Object(BUCKET_NAME, KEY).delete()
        try:
            s3.Object(BUCKET_NAME, "temp/" + execution_id).delete()
        except:
            print("No temp files to delete")
        # removing the local files
        os.remove(read_path)
        os.remove(write_path)
        record['status'] = "SUCCEEDED"
        return { "status":"SUCCEEDED"}