

<center>

# Translate Service

## Information about running this project<br><br></center>
Important Information

- Ensure you have Python Version 3+
- Node is installed
- npm cdk, is installed correctly for cdk
- npm react, is installed correctly for front-end
- <strong>Delete resources by running  `$ cdk destroy --all` , to avoid any running charges and confirm if the following resources were deleted by vising AWS Console</strong>

<br>

Configure AWS Account in your terminal

```
$ aws configure
```

<br>

Configure global constants in `_constants.py` if need to make any modifications

```
DEFAULT_REGION   = "YOUR_REGION" default: us-west-2
WHITE_LISTED_IPS = "YOUR_IPS"    default: AMAZON-CIDRS
```

<br>

### NOTE - Ensure you're in right path, `translate-service` when running the following commands<br><br>

Create Virtual Environment
```
$ python3 -m venv .venv
```

Activate Virtual Environment

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

<br>
Once the virtualenv is activated, you can install the required dependencies

```
$ pip3 install -r requirements.txt
```

If you have an additional profile, then please go to `cdk.json` and add the following code after "_app_"

```
"profile": "NAME_OF_YOUR_AWS_PROFILE"
```



Bootstrap the environment (installs required dependencies for react-front-end)

```
$ cd ../website && mkdir build && npm install react-scripts && cd ../translate-service/ && cdk bootstrap
```

Deploy `TranslateServiceStack` - Provisions infrastracture (API, IAM, Lambda, S3)

```
$ cdk deploy TranslateServiceStack --outputs-file ../website/src/secrets.json
```

Build prod for front-end after consuming outputs from `TranslateServiceStack`

```
$ cd ../website && npm run build && cd ../translate-service
```

Deploy `TranslateServiceWebStack` - Uploads prod web assets to website-bucket

```
$ cdk deploy TranslateServiceWebStack
```

<br><br>

---

<br><br>

# TranslateServiceStack

Following resources are provisioned (in-order of creation for dependecy purposes)

- S3
  - Batch Translate Bucket
  - Translate Service Bucket
- IAM Roles
  - Lambda Translate Role
  - Lambda Translate Doc/Batch Role
  - Lambda Translate Start Doc Role
  - Lambda Translate Document Role
  - Lambda List Files Role
  - Lambda File Download Role
  - SFN Translate Role
- Step Function
  - Document Translate (lambda)
  - Translate Document SM
- Lambda
  - Text Translator
  - Document URL Manager
  - Start Doc Translate
  - List Translated Files
  - Download Translated Files
- IAM Policies
  - _IAM Roles_
- API Gateway
  - Text
  - List Files
  - Doc
  - Download
- Outputs
  - API
    - Text
    - Doc
    - List Files
    - Download
  - Web Bucket ARN

<br>

## Detailed Information on resource <br><br>

### <u>Batch Translate Bucket</u>

<br> This bucket is used to store uploaded and translated documents

|              |                                                                                                                                         |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| _Defined as_ | `batch_bucket`                                                                                                                          |
| _Encryption_ | SSE Encrypted                                                                                                                           |
| _Policy_     | Only WHITE_LISTED_IPS defined in `_constants.py` are allowed to access                                                                  |
| _CORS_       | "PUT" allowed                                                                                                                           |
| _Other_      | Deploys assets from `batch_translate_bucket` directory where it containts empty files for folder creation & organization for processing |

<br>

### <u>Translate Service Bucket</u>

<br> This bucket is used to host a stactic website

|              |                                                                        |
| ------------ | ---------------------------------------------------------------------- |
| _Defined as_ | `my_web_bucket`                                                        |
| _Encryption_ | SSE Encrypted                                                          |
| _Policy_     | Only WHITE_LISTED_IPS defined in `_constants.py` are allowed to access |

<br>

### <u>Document Translate</u>

<br> This lambda function is used to translate documents using Amazon Translate(text).

|              |                                                                                |
| ------------ | ------------------------------------------------------------------------------ |
| _Defined as_ | `translate_document_lambda`                                                    |
| _Runtime_    | PYTHON_3.9++                                                                  |
| _Timeout_    | 15 minutes                                                                     |
| _Memory_     | 1024 mb                                                                        |
| _Handler_    | `translate_document.py`                                                        |
| _Role_       | Lambda Translate Document Role (`lambda_translate_document_role`)              |
| _Access_     | AWSLambdaBasicExecutionRole, TranslateReadOnly, s3: GET,PUT,LIST,DELETE,CREATE |

<br>

### <u>Translate Document SM</u>

<br> This step machine function is used to orchastrate flow of translating documents
| | |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|_Defined as_|`translate_document_sfn`|
| _Type_ | Standard|
| _Definition_ | - Submit Job (`submit_job`) - responsible for invoking `translate_document_lambda` along with event it recieved as input path <br> - Choice Job (`choice_job`) - checks if the function finished executing <br> - Wait Job (`wait_job`) - Default wait for 60 seconds, if still running function <br> - Succeed Job (`succeed_job`) - If execution output has _status_ = _SUCCEEDED_ then SFN if finished with execution, else it fails|
|_Role_|SFN Translate Role (`sfn_translate_doc_role`)|

<br>

### <u>Text Translator</u>

<br>This lambda function is used to translate text using Amazon Translate(text).
| | |
| ----------------------- | ------------------------------------------------------------------------- |
| _Defined as_ | `text_lambda` |
| _Runtime_ | PYTHON*3.9++ |
| \_Timeout* | 3 minutes(DEFAULT) |
| _Memory_ | 128 mb (DEFAULT) |
| _Handler_ | `text.py` |
| _Role_ | Lambda Translate Role (`lambda_translate_role`) |
| _Access_ | AWSLambdaBasicExecutionRole, TranslateReadOnly |

<br>

### <u>Document URL Manager</u>

<br> This lambda function is used to generate pre-signed URL to upload documents

|                         |                                                                           |
| ----------------------- | ------------------------------------------------------------------------- |
| _Defined as_            | `doc_lambda`                                                              |
| _Runtime_               | NODE_JS_16+                                                               |
| _Timeout_               | 3 minutes(DEFAULT)                                                        |
| _Memory_                | 128 mb (DEFAULT)                                                          |
| _Handler_               | `index.js`                                                                |
| _Environment Variables_ | `BATCH_BUCKET`                                                            |
| _Role_                  | Lambda Translate Batch Role(`lambda_translate_doc_role`)                  |
| _Access_                | [AWSLambdaBasicExecutionRole, batch_bucket - {GET,PUT,LIST,DELETE,CREATE} |

<br>

### <u>Start Doc Translate</u>

<br> This lambda function is used to evaluate an event for dropped file in (input/\*.txt) and invoke Translate Document SM

|                         |                                                                     |
| ----------------------- | ------------------------------------------------------------------- |
| _Defined as_            | `start_doc_lambda`                                                  |
| _Runtime_               | PYTHON_3.9+                                                         |
| _Timeout_               | 3 minutes(DEFAULT)                                                  |
| _Memory_                | 128 mb (DEFAULT)                                                    |
| _Handler_               | `start_step.py`                                                     |
| _Environment Variables_ | `BATCH_BUCKET, TRANSLATE_DOCUMENT_SFN_ARN`                          |
| _Role_                  | Lambda Translate Start Doc Role (`lambda_translate_start_doc_role`) |
| _Access_                | [AWSLambdaBasicExecutionRole, states:StartExecution]                |
| _Notification_          | `batch_bucket`; Add Object Created; Prefix (input/)                 |

<br>

### <u>List Translated Files</u>

<br>This lambda function is used to query objects in `batch_bucket/input/` and return a response in JSON

|                         |                                                                  |
| ----------------------- | ---------------------------------------------------------------- |
| _Defined as_            | `list_files_lambda`                                              |
| _Runtime_               | PYTHON_3.9+                                                      |
| _Timeout_               | 3 minutes(DEFAULT)                                               |
| _Memory_                | 128 mb (DEFAULT)                                                 |
| _Handler_               | `get_list_of_files.py`                                           |
| _Environment Variables_ | `BATCH_BUCKET`                                                   |
| _Role_                  | Lambda List Translated Documents Role (`lambda_list_files_role`) |
| _Access_                | [AWSLambdaBasicExecutionRole, AmazonS3ReadOnlyAccess]            |

<br>

### <u>Download Translated Files</u>

<br>This lambda function is used to generate a presigned-url after recieving filename from event to allow for downloads from S3 bucket

|                         |                                                         |
| ----------------------- | ------------------------------------------------------- |
| _Defined as_            | `download_file_lambda`                                  |
| _Runtime_               | NODE_JS_16+                                             |
| _Timeout_               | 3 minutes(DEFAULT)                                      |
| _Memory_                | 128 mb (DEFAULT)                                        |
| _Handler_               | `dwnld_translated_file.js`                              |
| _Environment Variables_ | `BATCH_BUCKET`                                          |
| _Role_                  | Lambda File Download Role (`lambda_file_download_role`) |
| _Access_                | [AWSLambdaBasicExecutionRole, s3:GetObject]             |

<br>

### <u>Translate Service - API Gateway</u>

<br>This is an API resource named, TranslateService, responsible for handling all the inbound/outbound API requests
| | |
| --------------- | ---------------- |
|_Defined as_|`base_api`|
| _Authorization_ | None |
| _Endpoint_ | Regional |
| _Resource Policy_ | execute-api:/* - WHITE_LISTED*IPS; execute-api:Invoke |
| Endpoints | check `_constants.py` e.g. [text,doc,list-files,download]|
| _Other_|Check code as certain resources are have Lambda Proxy while others are transformed thru API Gateway|

#

<br><br><br><br>
<br><br><br><br>
<br><br><br><br>

