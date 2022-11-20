import os
from aws_cdk import RemovalPolicy, Stack
from aws_cdk.aws_lambda import Function
from aws_cdk.aws_iam import (
    Effect,
    PolicyDocument,
    PolicyStatement,
    Role,
    ServicePrincipal,
)
from aws_cdk.aws_stepfunctions import (
    Credentials,
    DefinitionBody,
    StateMachine,
    StateMachineType,
    TaskRole,
)
from aws_cdk.aws_stepfunctions_tasks import LambdaInvoke
from constructs import Construct


class StepFunctionsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CDK_ACCOUNT_TRG = os.getenv("CDK_ACCOUNT_TRG")
        CDK_REGION_TRG = os.getenv("CDK_REGION_TRG")

        # Create reference (from ARN) to Lambda function in target account
        cross_account_lambda = Function.from_function_arn(
            self,
            "CrossAccountLambda",
            function_arn=f"arn:aws:lambda:{CDK_REGION_TRG}:{CDK_ACCOUNT_TRG}:function:cross-account-lambda",
        )

        # Create reference (from ARN) to Lambda invocation role in target account
        cross_account_lambda_role = Role.from_role_arn(
            self,
            "CrossAccountLambdaRole",
            role_arn=f"arn:aws:iam::{CDK_ACCOUNT_TRG}:role/cross-account-lambda-role",
        )

        # Create credentias for Lambda invoke task
        lambda_invoke_task_role = TaskRole.from_role(cross_account_lambda_role)
        lambda_invoke_task_credentials = Credentials(role=lambda_invoke_task_role)

        # Create Lambda invoke task
        lambda_invoke_task = LambdaInvoke(
            self,
            "LambdaInvokeTask",
            lambda_function=cross_account_lambda,
            credentials=lambda_invoke_task_credentials,
            retry_on_service_exceptions=False,
        )

        # Create policy document for state machine execution role
        cross_account_assume_role_policy_document = PolicyDocument(
            statements=[
                PolicyStatement(
                    effect=Effect.ALLOW,
                    actions=["sts:AssumeRole"],
                    resources=[
                        f"arn:aws:iam::{CDK_ACCOUNT_TRG}:role/cross-account-lambda-role",
                    ],
                )
            ]
        )

        # Create state machine execution role
        state_machine_role = Role(
            self,
            "StateMachineRole",
            role_name="state-machine-role",
            assumed_by=ServicePrincipal("states.amazonaws.com"),
            inline_policies={
                "cross-account-assume-role-policy": cross_account_assume_role_policy_document,
            },
        )

        # Create state machine
        StateMachine(
            self,
            "StateMachine",
            state_machine_name="state-machine",
            definition_body=DefinitionBody.from_chainable(lambda_invoke_task),
            role=state_machine_role,
            state_machine_type=StateMachineType.STANDARD,
            removal_policy=RemovalPolicy.DESTROY,
        )
