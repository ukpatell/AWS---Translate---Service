<center>

# Backlog - Translate Service
</center>

### This file compiles numberous valuable feedback recieved from Mentors, Accounts Team and other AWS professionals to enhance the current state of this application

<br><br>
|Priority|Short|Description|
|-|-|-|
|1|Pre-signed URL|Current Application uses pre-signed urls to upload & download documents. Use of pre-signed urls can only be created using CLI in GovCloud. Our application currently uses Lambda to generate it|
|2|Authentication|Currently, there is no authentication fronting our webapp. Cognito code is already commented in `translate_service_stack.py`, however it can't be implemented as static url from s3 is not **https** (SSL). Cognito isn't available in **us-east** with advanced security feature and therefore needs to use thrid-party auth providers like *key cloak*| 
|3|Business Logic|In its current state, there are minor hiccups when handling documents of sizes > 1mb due to timeouts and throttling. Need a better way to handle, use of buffer & multi-threading may help the application and be efficient|
|4|Live Estimate|Being able to provide this service for our customer to provide a live individual cost (estimate) for a file they upload for US only. Restricting download to prevent this service from being "free" |
|5|Comprehend|Providing the ability give sentiment data on document/text a user submits for translation would be enhanced feature|
|6|Polly|An ability to text-to-speech with other feature such as choosing narrator etc.|
|7|Image Translation|This use case can be debated based on the needs of customers. Taking an image, translating the text (use Textract or other python libraries), and replace the text from the image as best as possible or draw a rough area. Or else, provide the just the translated text without replacing it on the image.
|8|Website Translation|Webite translation is supported by Translate but there might challenges in handling web tags|
|9|Large File & Size|Supporting various file formats (ppt, csv, xlf, docx) and/or increased size upto 5GB or another reasonable amount to avoid unexpected higher costs|
|10|Custom Text|Adding the ability to support other custom features of text translate such as Formality and Masking based on the source/target language|
|11|Active Custom Translate|Customized Machine Translation with named entity etc.|
|12|Confidence Score|Provide confidence on translation output. Comprehend supports more languages than those that are supported by Amazon Translate and so therefore it is important and there is a chance of comprehend picking up a language not supported by Amazon Translate using *auto* detection|
|13|User Persona|Allowing customers the ability to add their user persona so it's more dynamic|

<br><br><br>

### Other
* Drag and Drop functionality for document handling
* Progress bar for translations
* Notification if translation job - [ SUCCEEDED, FAILED, RUNNING ]
    * If failed, provide response, the amount of translation done before it failed
* Lifecycle policies for "uploaded" documents to save on costs / more control
* Delete / share translated files 


