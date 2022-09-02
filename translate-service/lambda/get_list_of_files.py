import json
import boto3
import os


s3client = boto3.client("s3")
s3 = boto3.resource('s3')
BUCKET_NAME = os.environ['BATCH_BUCKET']
def lambda_handler(event, context):
    file_name, file_code = [], []
    language_codes = {'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan', 'zh': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'fa-AF': 'Dari', 'nl': 'Dutch', 'en': 'English', 'et': 'Estonian', 'fa': 'Farsi (Persian)', 'tl': 'Filipino, Tagalog', 'fi': 'Finnish', 'fr': 'French', 'fr-CA': 'French (Canada)', 'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'he': 'Hebrew', 'hi': 'Hindi', 'hu': 'Hungarian', 'is': 'Icelandic', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian', 'ja': 'Japanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'ko': 'Korean', 'lv': 'Latvian', 'lt': 'Lithuanian', 'mk': 'Macedonian', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mr': 'Marathi', 'mn': 'Mongolian', 'no': 'Norwegian', 'ps': 'Pashto', 'pl': 'Polish', 'pt': 'Portuguese (Brazil)', 'pt-PT': 'Portuguese (Portugal)', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian', 'sr': 'Serbian', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'es-MX': 'Spanish (Mexico)', 'sw': 'Swahili', 'sv': 'Swedish', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh'}
    
    response = s3client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="output")
    for key in (response['Contents']):
        name = key.get('Key')
        object_name = name.split("/")[-1]
        file_extension = object_name.split(".")[-1]
        if file_extension in ["txt", "TXT", "text", "TEXT"]:
            file_name.append(object_name)
            code = s3client.head_object(Bucket=BUCKET_NAME, Key=name)['Metadata']['target']
            language = language_codes.get(code)
            file_code.append(language)
            
    final_response = [{"Name":f, "Code":c} for f,c in zip(file_name,file_code)]
    return final_response

 