from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3_notifications as s3_notify,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_cognito as cognito,
    RemovalPolicy,
    )
from constructs import Construct
import aws_cdk as cdk
from ._constants import *



class TranslateServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs,termination_protection=False, description="CDK Stack for Deploying Infrastructure and Application Code")
        
        #------------------------ S3 Buckets------------------------#
        
        # Bucket for Batch Translation (Input / Output)
        batch_bucket = s3.Bucket(self,"batch_translate_bucket",
                                  removal_policy=RemovalPolicy.DESTROY,
                                  encryption=s3.BucketEncryption.S3_MANAGED,
                                  auto_delete_objects=True,
                                  cors=[s3.CorsRule(
                                            allowed_headers=["*"],
                                            allowed_methods=[s3.HttpMethods.PUT],
                                            allowed_origins=["*"])
                                        ])
        
        # Add bucket policies
        result = batch_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            resources = [
                f"{batch_bucket.bucket_arn}/*"
            ],
            actions = [
                "s3:GetObject",
                "s3:PutObject"
            ],
            principals = [
                iam.AnyPrincipal()
            ],
            conditions = {
                            "IpAddress": {
                                "aws:SourceIp": WHITE_LISTED_IPS
                            }
            }
        ))
        # Deploy the website assets to the bucket
        deployment = s3deploy.BucketDeployment(self,"deploy-website",
                                               sources=[s3deploy.Source.asset("./batch_translate_bucket")],
                                               destination_bucket=batch_bucket)
        
        
         # THIS BUCKET IS CREATED FOR WEBSITE DEPLOYMENT
        my_web_bucket = s3.Bucket(self,"translate-service-bucket",
                                  removal_policy=RemovalPolicy.DESTROY,
                                  auto_delete_objects=True,
                                  website_index_document="index.html",
                                  encryption=s3.BucketEncryption.S3_MANAGED)
        # Add bucket policies
        my_web_bucket_result = my_web_bucket.add_to_resource_policy(iam.PolicyStatement(
            effect = iam.Effect.ALLOW,
            resources = [
                f"{my_web_bucket.bucket_arn}/*"
            ],
            actions = [
                "s3:GetObject"
            ],
            principals = [
                iam.AnyPrincipal()
            ],
            conditions = {
                            "IpAddress": {
                                "aws:SourceIp": WHITE_LISTED_IPS,
                            }
            }
        ))
        
        
        #----------------------------IAM Roles---------------------------#
        
        # Role for Lambda Function
        lambda_translate_role = iam.Role(self,"Lambda Translate Role",
                                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        
        # Role for Lambda S3 Signed URL for Batch File
        lambda_translate_doc_role = iam.Role(self,"Lambda Translate Batch Role",
                                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        
        # Role for Lambda Document Translate Invoke
        lambda_translate_start_doc_role = iam.Role(self,"Lambda Translate Document SFN Role",
                                                   assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        
        # Role for Performing Lambda Document Translation
        lambda_translate_document_role = iam.Role(self,"Lambda Translate Document Role",
                                                   assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        
        #Role for Obtaining List of Files(Translated)
        lambda_list_files_role = iam.Role(self,"Lambda List Translated Documents Role",
                                                   assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        
        # Role for Lambda S3 Signed URL for Downloading File
        lambda_file_download_role = iam.Role(self,"Lambda Translate File Download Role",
                                        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        
        # Role for Tranlate Doc Step Function 
        sfn_translate_doc_role = iam.Role(self,"SFN Translate Role",
                                          assumed_by=iam.ServicePrincipal("states.amazonaws.com"))
        
                                 
        #------------------------Step Functions------------------------#
        
        # Lambda Function for Performing Document Translations
        translate_document_lambda = _lambda.Function(
                self, 'Document_Translate',
                runtime=_lambda.Runtime.PYTHON_3_9,
                code=_lambda.Code.from_asset('lambda'),
                handler='translate_document.lambda_handler',
                role=lambda_translate_document_role,
                environment=dict(BATCH_BUCKET=batch_bucket.bucket_name),
                memory_size =1024,
                timeout=cdk.Duration.minutes(15)     
        )
        
        # Step Function Definition
        
        submit_job = tasks.LambdaInvoke(
                self,"submitTranslateDocuments",
                lambda_function=translate_document_lambda,
                input_path="$.Records",
        )
        
        choice_job = sfn.Choice(
            self, "Is it done yet?"
        )
        
        wait_job = sfn.Wait(
            self,"Wait for 60 seconds",
            time=sfn.WaitTime.duration(
                Duration.seconds(60))
        )
        
        succeed_job=sfn.Succeed(
            self,"Succeeded",
            comment='Translation Successful'
        )
        
        definition = submit_job.next(choice_job.when(sfn.Condition.string_equals('$.Payload.status', 'SUCCEEDED'), succeed_job).otherwise(wait_job.next(submit_job)))
        
        # Create state machine
        translate_document_sfn = sfn.StateMachine(
            self, "TranslateDocumentSM",
            definition=definition,
            role=sfn_translate_doc_role,
        )
        
        #------------------------Lambda Functions------------------------#
        
        # Lambda Function for Text Translations
        text_lambda = _lambda.Function(
            self, 'Text_Translator',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='text.lambda_handler',
            role=lambda_translate_role,
        )
        
        # Lambda Function for Document Translations
        doc_lambda = _lambda.Function(
            self, 'Document_Url_Manager',
            runtime=_lambda.Runtime.NODEJS_16_X,
            code=_lambda.Code.from_asset('lambda'),
            handler='index.handler',
            role=lambda_translate_doc_role,
            environment=dict(BATCH_BUCKET=batch_bucket.bucket_name)
        )
        
        
        # Lambda Function for Starting Doc Translations SFN Workflow
        start_doc_lambda = _lambda.Function(
            self, 'Start_Doc_Translate',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='start_step.lambda_handler',
            role=lambda_translate_start_doc_role,
            environment=dict(BATCH_BUCKET=batch_bucket.bucket_name,TRANSLATE_DOCUMENT_SFN_ARN=translate_document_sfn.state_machine_arn)
        )
        
        ###### Dropped Files in Input - Create trigger for Lambda function
        notification = s3_notify.LambdaDestination(start_doc_lambda)
        notification.bind(self, batch_bucket)        
        
        ###### Add Create Event only for .jpg files
        batch_bucket.add_object_created_notification(
           notification, s3.NotificationKeyFilter(prefix='input/'))
        
        # Lambda Function for Listing Translated Files
        list_files_lambda = _lambda.Function(
            self, 'List_Translated_Files',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('lambda'),
            handler='get_list_of_files.lambda_handler',
            role=lambda_list_files_role,
            environment=dict(BATCH_BUCKET=batch_bucket.bucket_name),
        )
        
        # Lambda Function for Downloading Translated Files
        download_file_lambda = _lambda.Function(
            self, 'Download_Translated_Files',
            runtime=_lambda.Runtime.NODEJS_16_X,
            code=_lambda.Code.from_asset('lambda'),
            handler='dwnld_translated_file.handler',
            role=lambda_file_download_role,
            environment=dict(BATCH_BUCKET=batch_bucket.bucket_name),
        )
        
        #----------------------------IAM Policies---------------------------#
        
        # Attach role(s) extended to basic Lambda Function/Execution Access - TEXT_LAMBDA
        text_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_translate_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_translate_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("TranslateReadOnly"))
        
        # Attach role(s) extended to basic Lambda Function/Execution Access - DOC_LAMBDA
        doc_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_translate_doc_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_translate_doc_role.attach_inline_policy(iam.Policy(self,"translate-ui-doc-translate-policy",
                        statements = [iam.PolicyStatement(
                        effect = iam.Effect.ALLOW,
                        resources = [
                            f"{batch_bucket.bucket_arn}",
                            f"{batch_bucket.bucket_arn}/*"
                        ],
                        actions = [
                            "s3:PutObject",
                            "s3:GetObject",
                            "s3:ListBucket",
                            "s3:DeleteObject",
                            "s3:CreateObject",
                        ])
            ],
        ))
        
        # Attach role(s) extended to basic Lambda Function/Execution Access - START_DOC_LAMBDA
        start_doc_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_translate_start_doc_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_translate_start_doc_role.attach_inline_policy(iam.Policy(self,"translate-ui-start-doc-sfn-translate-policy",
                        statements = [iam.PolicyStatement(
                        effect = iam.Effect.ALLOW,
                        resources = [
                            f"{translate_document_sfn.state_machine_arn}*",
                        ],
                        actions = ["states:StartExecution",
                        ])
            ],
        ))
        
        # Attach role(s) extended to Step Functions - translate_document_sfn
        translate_document_sfn.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        sfn_translate_doc_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        sfn_translate_doc_role.attach_inline_policy(iam.Policy(self,"translate-ui-sfn-translate-doc-policy",
                        statements = [
                            iam.PolicyStatement(
                                effect = iam.Effect.ALLOW,
                                resources = [
                                    f"{translate_document_lambda.function_arn}",
                                ],
                                actions = ["Lambda:InvokeFunction"]),
                            iam.PolicyStatement(
                                effect = iam.Effect.ALLOW,
                                resources = [
                                    f"{translate_document_sfn.state_machine_arn}",
                                ],
                                actions = ["states:StartExecution","states:StopExecution"]),
                        ],
        ))
        
        # Attach role(s) extended for Document Translate for Lambda Function - 
        translate_document_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_translate_document_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_translate_document_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("TranslateReadOnly"))
        lambda_translate_document_role.attach_inline_policy(iam.Policy(self,"translate-ui-document-translate-policy",
                        statements = [iam.PolicyStatement(
                        effect = iam.Effect.ALLOW,
                        resources = [
                            f"{batch_bucket.bucket_arn}",
                            f"{batch_bucket.bucket_arn}/*"
                        ],
                        actions = [
                            "s3:PutObject",
                            "s3:GetObject",
                            "s3:ListBucket",
                            "s3:DeleteObject",
                            "s3:CreateObject",
                        ])
            ],
        ))
        
        # Attach role(s) extended to basic Lambda Function/Execution Access - LIST OF TRANSLATED FILES
        list_files_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_list_files_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_list_files_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))
        
        # Attach role(s) extended to basic Lambda Function/Execution Access - DOWNLOAD FILE
        download_file_lambda.apply_removal_policy(cdk.RemovalPolicy.DESTROY)
        lambda_file_download_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))
        lambda_file_download_role.attach_inline_policy(iam.Policy(self,"translate-ui-dwnld-file",
                        statements = [iam.PolicyStatement(
                        effect = iam.Effect.ALLOW,
                        resources = [
                            f"{batch_bucket.bucket_arn}/*",
                        ],
                        actions = [
                            "s3:GetObject",
                        ])
            ],
        ))
        
        #-----------------------API GATEWAY------------------------# 
        
              
        ######## BASE API
        api_resource_policy = iam.PolicyDocument(
            statements=[iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    resources = [
                        "execute-api:/*"
                    ],
                    actions = [
                        "execute-api:Invoke",
                    ],
                    principals = [
                        iam.AnyPrincipal()
                    ],
                    conditions = {
                                    "IpAddress": {
                                        "aws:SourceIp": WHITE_LISTED_IPS
                                    }
                    }
                )]
            )
        
        base_api = apigateway.RestApi(self,'TranslateService',
                                      endpoint_types=[apigateway.EndpointType.REGIONAL],
                                      policy=api_resource_policy,
                                      )
        
        
        #------- API / Text - Text Translation
        text_resource = base_api.root.add_resource(
            API_TEXT_RESOURCE,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['POST', 'OPTIONS'],
                allow_origins=apigateway.Cors.ALL_ORIGINS)
        )
        text_lambda_integration = apigateway.LambdaIntegration(
            text_lambda,
            proxy=False,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        text_resource.add_method(
            'POST', text_lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
        
         #------- API / List Files (Translated)
        list_resource = base_api.root.add_resource(
            API_LIST_RESOURCE,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['GET'],
                allow_origins=apigateway.Cors.ALL_ORIGINS)
        )
        get_list_of_files_lambda_integration = apigateway.LambdaIntegration(
            list_files_lambda,
            proxy=False,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        list_resource.add_method(
            'GET', get_list_of_files_lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
        
        # API / Doc - Document Upload
        doc_resource = base_api.root.add_resource(
            API_DOC_RESOURCE,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['GET','PUT'],
                allow_origins=apigateway.Cors.ALL_ORIGINS)
        )
        doc_lambda_integration = apigateway.LambdaIntegration(
            doc_lambda,
            proxy=True,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        doc_resource.add_method(
            'GET', doc_lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    },
                )
            ]
        )
        
        # API / Doc - Download File
        doc_dwnld_resource = base_api.root.add_resource(
            API_DWNLD_RESOURCE,
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_methods=['GET', 'POST'],
                allow_origins=apigateway.Cors.ALL_ORIGINS)
        )
        doc_dwnld_lambda_integration = apigateway.LambdaIntegration(
            download_file_lambda,
            proxy=True,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': "'*'"
                    }
                )
            ]
        )
        doc_dwnld_resource.add_method(
            'GET',doc_dwnld_lambda_integration,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_parameters={
                        'method.response.header.Access-Control-Allow-Origin': True
                    }
                )
            ]
        )
        
        
        #------------------------OUTPUTS & EXPORTS------------------------#
        

        # Export API URL for TEXT TRANSLATE
        cdk.CfnOutput(self, 'API-URL-TRANSLATE-DOC',value=base_api.url+API_DOC_RESOURCE, description="API URL: Translate Doc & Upload for PS-URL", export_name="API-URL-TRANSLATE-DOC")
        cdk.CfnOutput(self, 'API-URL-TRANSLATE-TEXT',value=base_api.url+API_TEXT_RESOURCE, description="API URL: Translate Text", export_name="API-URL-TRANSLATE-TEXT")
        cdk.CfnOutput(self, 'API-URL-LIST-TRANSLATED-FILES',value=base_api.url+API_LIST_RESOURCE, description="API URL: List Translated Files", export_name="API-URL-LIST-TRANSLATED-FILES")
        cdk.CfnOutput(self, 'API-URL-DWNLD-TRANSLATED-FILES',value=base_api.url+API_DWNLD_RESOURCE, description="API URL: Download Translated Files", export_name="API-URL-DWNLD-TRANSLATED-FILES")
        cdk.CfnOutput(self, 'WEB_URL',value=my_web_bucket.bucket_website_url, description="This is the URL for the Translate Website", export_name="WEB-URL")
        cdk.CfnOutput(self, 'WEB-BUCKET-ARN',value=my_web_bucket.bucket_arn, description="Static Website ARN", export_name="WEB-BUCKET-ARN")
        
        
        
        # cdk.CfnOutput(self, 'USER-POOL',value=user_pool.ref, description="User Pool w. Cognito for Translate", export_name="USER-POOL")
        # cdk.CfnOutput(self, 'USER-POOL-CLIENT-ID',value=user_pool_client.ref, description="User Pool Client w. Cognito for Translate", export_name="USER-POOL-CLIENT-ID")
        # cdk.CfnOutput(self, 'IDENTITY-POOL',value=identity_pool.ref, description="Identity Pool w. Cognito for Translate", export_name="IDENTITY-POOL")
        
        
        
    
        #----------------------- COGNITO ------------------------# 
        
        
        # user_pool = cognito.CfnUserPool(self, "translate-user-pool",
        #     schema=[
        #         cognito.CfnUserPool.SchemaAttributeProperty(
        #             name="email",
        #             required=True,
        #             mutable=False
        #         ),
        #         cognito.CfnUserPool.SchemaAttributeProperty(
        #             name="email_verified",
        #             required=True,
        #             mutable=True
        #         )
        #     ]
        # )

        # user_pool_client = cognito.CfnUserPoolClient(self, "TranslateClient",
        #     user_pool_id=user_pool.ref,
        #     allowed_o_auth_flows_user_pool_client=True,
        #     allowed_o_auth_flows=["implicit"],
        #     allowed_o_auth_scopes=["email", "openid"],
        #     generate_secret=False,
        #     callback_ur_ls=[f"{my_web_bucket.bucket_website_url}/auth","http://localhost:3000/auth"]
        # )
        # user_pool_client.add_property_override("RefreshTokenValidity", 1)
        # user_pool_client.add_property_override("SupportedIdentityProviders", ["COGNITO"])
        
        # cfn_user_pool_domain = cognito.CfnUserPoolDomain(self, "AWSTranslateCognitoDomain",
        #     user_pool_id=user_pool.ref,
        #     domain="translate-domain",
        # )
        
        # cfn_user_pool_user = cognito.CfnUserPoolUser(self, "Translate-DefaultUserPoolUser",
        #     user_pool_id=user_pool.ref,
        #     force_alias_creation=False,
        #     username="TranslateDay1",
        #     user_attributes=[
        #         cognito.CfnUserPoolUser.AttributeTypeProperty(
        #             name="email_verified",
        #             value="true"
        #         ),
        #         cognito.CfnUserPoolUser.AttributeTypeProperty(
        #             name="email",
        #             value=email.value_as_string,
        #         ),
        #     ]
        # )

        # identity_pool = cognito.CfnIdentityPool(self, "translate-identity-pool",
        #     allow_unauthenticated_identities=True,
        #     cognito_identity_providers=[cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
        #         client_id=user_pool_client.ref,
        #         provider_name=user_pool.attr_provider_name
        #     )]
        # )
        
        # unauth_role = iam.Role(self, "TranslateCognitoUnauthRole",
        #     assumed_by=iam.FederatedPrincipal(
        #         "cognito-identity.amazonaws.com",
        #         {
        #             "StringEquals": {
        #                 "cognito-identity.amazonaws.com:aud": identity_pool.ref,
        #             },
        #             "ForAnyValue:StringLike": {
        #                 "cognito-identity.amazonaws.com:amr": "unauthenticated",
        #             },
        #         },
        #         "sts:AssumeRoleWithWebIdentity"
        #     ),
        #     description="Default role for Unauthenticated Cognito User(s)"
        # )

        # auth_role = iam.Role(self, "TranslateCognitoAuthRole",
        #     assumed_by=iam.FederatedPrincipal(
        #         "cognito-identity.amazonaws.com",
        #         {
        #             "StringEquals": {
        #                 "cognito-identity.amazonaws.com:aud": identity_pool.ref,
        #             },
        #             "ForAnyValue:StringLike": {
        #                 "cognito-identity.amazonaws.com:amr": "authenticated",
        #             },
        #         },
        #         "sts:AssumeRoleWithWebIdentity"
        #     ),
        #     description="Default role for Unauthenticated Cognito User(s)"
        # )

        # # Allow read write to input bucket
        # unauth_role.add_to_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         actions=[
        #             "s3:GetObject",
        #         ],
        #         resources=[
        #             f"{my_web_bucket.bucket_arn}/*"
        #         ],
        #         conditions = {
        #                     "IpAddress": {
        #                         "aws:SourceIp": WHITE_LISTED_IPS,
        #                     }
        #         }
        #     )
        # )

        # identity_pool_role_attachment = cognito.CfnIdentityPoolRoleAttachment(self, "IdentityPoolRoleAttachment",
        #     identity_pool_id=identity_pool.ref,
        #     roles={
        #         "authenticated": auth_role.role_arn,
        #         "unauthenticated": unauth_role.role_arn
        #     },
        #     role_mappings={
        #         'cognito-user-pool': cognito.CfnIdentityPoolRoleAttachment.RoleMappingProperty(
        #             type='Token',
        #             ambiguous_role_resolution='AuthenticatedRole',
        #             identity_provider=f'cognito-idp.{Stack.of(self).region}.amazonaws.com/{user_pool.ref}:{user_pool_client.ref}'
        #         )
        #     }
        # )