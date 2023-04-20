import os
from aws_cdk import (
    RemovalPolicy,
    Stack,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as sfn_tasks,
)
from constructs import Construct


class StepFunctionsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        AWS_ACCOUNT_ID_TRG = os.getenv("AWS_ACCOUNT_ID_TRG")
        AWS_REGION_TRG = os.getenv("AWS_REGION_TRG")

        # Create reference (from ARN) to lambda function in target account
        cross_account_lambda = _lambda.Function.from_function_arn(
            self,
            "CrossAccountLambda",
            function_arn=f"arn:aws:lambda:{AWS_REGION_TRG}:{AWS_ACCOUNT_ID_TRG}:function:cross-account-lambda",
        )

        # Create reference (from ARN) to lambda invocation role in target account
        cross_account_lambda_invocation_role = iam.Role.from_role_arn(
            self,
            "CrossAccountLambdaInvocationRole",
            role_arn=f"arn:aws:iam::{AWS_ACCOUNT_ID_TRG}:role/cross-account-lambda-invocation-role",
        )

        # Create credentias for lambda invoke task
        lambda_invoke_task_role = sfn.TaskRole.from_role(cross_account_lambda_invocation_role)
        lambda_invoke_task_credentials = sfn.Credentials(role=lambda_invoke_task_role)

        # Create lambda invoke task
        lambda_invoke_task = sfn_tasks.LambdaInvoke(
            self,
            "LambdaInvokeTask",
            lambda_function=cross_account_lambda,
            credentials=lambda_invoke_task_credentials,
            retry_on_service_exceptions=False,
        )

        # Create policy document for state machine execution role
        cross_account_assume_role_policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["sts:AssumeRole"],
                    resources=[
                        f"arn:aws:iam::{AWS_ACCOUNT_ID_TRG}:role/cross-account-lambda-invocation-role",
                    ],
                )
            ]
        )

        # Create state machine execution role
        state_machine_execution_role = iam.Role(
            self,
            "Role_state-machine-execution-role",
            role_name="state-machine-execution-role",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
            inline_policies={
                "cross-account-assume-role-policy": cross_account_assume_role_policy_document,
            },
        )

        # Create state machine
        state_machine = sfn.StateMachine(
            self,
            "StateMachine_state-machine",
            state_machine_name="state-machine",
            definition=lambda_invoke_task,
            role=state_machine_execution_role,
            state_machine_type=sfn.StateMachineType.STANDARD,
            removal_policy=RemovalPolicy.DESTROY,
        )
