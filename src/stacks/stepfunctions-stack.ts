import { RemovalPolicy, Stack, StackProps } from "aws-cdk-lib";
import {
  Effect,
  PolicyDocument,
  PolicyStatement,
  Role,
  ServicePrincipal,
} from "aws-cdk-lib/aws-iam";
import { Function } from "aws-cdk-lib/aws-lambda";
import {
  DefinitionBody,
  StateMachine,
  StateMachineType,
  TaskRole,
} from "aws-cdk-lib/aws-stepfunctions";
import { LambdaInvoke } from "aws-cdk-lib/aws-stepfunctions-tasks";
import { Construct } from "constructs";
import { validateEnv } from "../utils/validate-env";

const env = validateEnv(["CDK_ACCOUNT_TRG", "CDK_REGION_TRG"]);

export class StepfunctionsStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Reference to Lambda function in target account
    const crossAccountLambda = Function.fromFunctionArn(
      this,
      "CrossAccountLambda",
      `arn:aws:lambda:${env.CDK_REGION_TRG}:${env.CDK_ACCOUNT_TRG}:function:cross-account-lambda`,
    );

    // Reference to Lambda invocation role in target account
    const crossAccountLambdaRole = Role.fromRoleArn(
      this,
      "CrossAccountLambdaRole",
      `arn:aws:iam::${env.CDK_ACCOUNT_TRG}:role/cross-account-lambda-role`,
    );

    // Create Lambda invoke task with cross-account credentials
    const lambdaInvokeTask = new LambdaInvoke(this, "LambdaInvokeTask", {
      lambdaFunction: crossAccountLambda,
      credentials: {
        role: TaskRole.fromRole(crossAccountLambdaRole),
      },
      retryOnServiceExceptions: false,
    });

    // Create policy document for state machine execution role
    const crossAccountAssumeRolePolicyDocument = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["sts:AssumeRole"],
          resources: [
            `arn:aws:iam::${env.CDK_ACCOUNT_TRG}:role/cross-account-lambda-role`,
          ],
        }),
      ],
    });

    // Create state machine execution role
    const stateMachineRole = new Role(this, "StateMachineRole", {
      roleName: "state-machine-role",
      assumedBy: new ServicePrincipal("states.amazonaws.com"),
      inlinePolicies: {
        "cross-account-assume-role-policy":
          crossAccountAssumeRolePolicyDocument,
      },
    });

    // Create state machine
    new StateMachine(this, "StateMachine", {
      stateMachineName: "state-machine",
      definitionBody: DefinitionBody.fromChainable(lambdaInvokeTask),
      role: stateMachineRole,
      stateMachineType: StateMachineType.STANDARD,
      removalPolicy: RemovalPolicy.DESTROY,
    });
  }
}
