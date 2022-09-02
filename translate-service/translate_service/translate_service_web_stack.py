from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
)
from constructs import Construct
import aws_cdk as cdk

class TranslateServiceWebStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs,termination_protection=False, description="CDK Stack for Website Deployment")

        
        #------------------------S3 Bucket Website Hosting------------------------#

       # Deploy the website assets to the bucket
        bucket_arn = cdk.Fn.import_value('WEB-BUCKET-ARN')
        my_web_bucket = s3.Bucket.from_bucket_arn(self,"existing-web-bucket",bucket_arn)

        
        deployment = s3deploy.BucketDeployment(self,"deploy-website",
                                               sources=[s3deploy.Source.asset("../website/build")],
                                               destination_bucket=my_web_bucket)

