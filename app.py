import os
from aws_cdk import App, Environment
from cdk_aws_cross_account_lambda.stacks.lambda_stack import LambdaStack
from cdk_aws_cross_account_lambda.stacks.stepfunctions_stack import (
    StepFunctionsStack,
)


def get_env_variable(name):
    """
    Helper function to get an environment variable.
    Raises an exception if the environment variable is not found.
    """
    value = os.getenv(name)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is not defined.")
    return value


### ENVIRONMENTS ###

src_env = Environment(
    account=get_env_variable("CDK_ACCOUNT_SRC"),
    region=get_env_variable("CDK_REGION_SRC"),
)

trg_env = Environment(
    account=get_env_variable("CDK_ACCOUNT_TRG"),
    region=get_env_variable("CDK_REGION_TRG"),
)

### APP ###

app = App()

StepFunctionsStack(
    app,
    "src",
    stack_name="StepFunctionsStack-src",
    env=src_env,
)

LambdaStack(
    app,
    "trg",
    stack_name="LambdaStack-trg",
    env=trg_env,
)

app.synth()
