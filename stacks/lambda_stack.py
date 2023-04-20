import os
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
)
from constructs import Construct


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        AWS_ACCOUNT_ID_SRC = os.getenv("AWS_ACCOUNT_ID_SRC")
        AWS_REGION_SRC = os.getenv("AWS_REGION_SRC")
        AWS_ACCOUNT_ID_TRG = os.getenv("AWS_ACCOUNT_ID_TRG")
        AWS_REGION_TRG = os.getenv("AWS_REGION_TRG")

        # Create policy document for cross-account lambda invocation role
        cross_account_lambda_invocation_policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["lambda:InvokeFunction"],
                    resources=[
                        f"arn:aws:lambda:{AWS_REGION_TRG}:{AWS_ACCOUNT_ID_TRG}:function:cross-account-lambda",
                    ],
                )
            ]
        )

        # Create role for cross-account lambda invocation
        cross_account_lambda_invocation_role = iam.Role(
            self,
            "Role_cross-account-lambda-invocation-role",
            role_name="cross-account-lambda-invocation-role",
            assumed_by=iam.ArnPrincipal(
                f"arn:aws:iam::{AWS_ACCOUNT_ID_SRC}:role/state-machine-execution-role"
            ),
            external_ids=[
                f"arn:aws:states:{AWS_REGION_SRC}:{AWS_ACCOUNT_ID_SRC}:stateMachine:state-machine"
            ],
            inline_policies={
                "cross-account-lambda-invocation-policy": cross_account_lambda_invocation_policy_document,
            },
        )

        # Create cross-account lambda function
        cross_account_lambda = _lambda.Function(
            self,
            "LambdaFunction_cross-account-lambda",
            function_name="cross-account-lambda",
            code=_lambda.Code.from_asset("lambda/functions/cross-account-lambda"),
            handler="lambda_function.lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_10,
        )
