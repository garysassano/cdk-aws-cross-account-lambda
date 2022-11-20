import os
from pathlib import Path
from aws_cdk import Stack
from aws_cdk.aws_iam import ArnPrincipal, Effect, PolicyDocument, PolicyStatement, Role
from aws_cdk.aws_lambda import Code, Function, Runtime
from constructs import Construct


class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CDK_ACCOUNT_SRC = os.getenv("CDK_ACCOUNT_SRC")
        CDK_REGION_SRC = os.getenv("CDK_REGION_SRC")
        CDK_ACCOUNT_TRG = os.getenv("CDK_ACCOUNT_TRG")
        CDK_REGION_TRG = os.getenv("CDK_REGION_TRG")

        # Create policy document for cross-account Lambda invocation
        cross_account_lambda_role_policy_document = PolicyDocument(
            statements=[
                PolicyStatement(
                    effect=Effect.ALLOW,
                    actions=["lambda:InvokeFunction"],
                    resources=[
                        f"arn:aws:lambda:{CDK_REGION_TRG}:{CDK_ACCOUNT_TRG}:function:cross-account-lambda",
                    ],
                )
            ]
        )

        # Create role for cross-account Lambda invocation
        Role(
            self,
            "CrossAccountLambdaRole",
            role_name="cross-account-lambda-role",
            assumed_by=ArnPrincipal(
                f"arn:aws:iam::{CDK_ACCOUNT_SRC}:role/state-machine-role"
            ),
            external_ids=[
                f"arn:aws:states:{CDK_REGION_SRC}:{CDK_ACCOUNT_SRC}:stateMachine:state-machine"
            ],
            inline_policies={
                "cross-account-lambda-invocation-policy": cross_account_lambda_role_policy_document,
            },
        )

        # Create cross-account Lambda function
        Function(
            self,
            "CrossAccountLambda",
            function_name="cross-account-lambda",
            code=Code.from_asset(
                str(Path(__file__).parent / ".." / "functions" / "cross-account")
            ),
            handler="index.handler",
            runtime=Runtime.PYTHON_3_12,
        )
