import os
import aws_cdk as cdk
from constructs import Construct
from stacks.lambda_stack import LambdaStack
from stacks.stepfunctions_stack import StepFunctionsStack

app = cdk.App()

StepFunctionsStack(
    app,
    "source",
    stack_name="StepFunctionsStack-source",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)

LambdaStack(
    app,
    "target",
    stack_name="LambdaStack-target",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region=os.environ.get("CDK_DEFAULT_REGION"),
    ),
)

app.synth()
