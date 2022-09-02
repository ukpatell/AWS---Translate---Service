#!/usr/bin/env python3
import os
import aws_cdk as cdk

from translate_service.translate_service_stack import TranslateServiceStack
from translate_service.translate_service_web_stack import TranslateServiceWebStack

from translate_service._constants import DEFAULT_REGION

app = cdk.App()

TranslateServiceStack(app, "TranslateServiceStack",
                      env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=DEFAULT_REGION),
                      )
TranslateServiceWebStack(app, "TranslateServiceWebStack",
                         env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),region=DEFAULT_REGION),
                         )

app.synth()
