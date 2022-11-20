import { Duration, Stack, StackProps } from "aws-cdk-lib";
import {
  ArnPrincipal,
  Effect,
  PolicyDocument,
  PolicyStatement,
  Role,
} from "aws-cdk-lib/aws-iam";
import { Architecture, LoggingFormat, Runtime } from "aws-cdk-lib/aws-lambda";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import { Construct } from "constructs";
import { join } from "path";
import { validateEnv } from "../utils/validate-env";

const env = validateEnv([
  "CDK_ACCOUNT_SRC",
  "CDK_REGION_SRC",
  "CDK_ACCOUNT_TRG",
  "CDK_REGION_TRG",
]);

export class LambdaStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Create policy document for cross-account Lambda invocation
    const crossAccountLambdaRolePolicyDocument = new PolicyDocument({
      statements: [
        new PolicyStatement({
          effect: Effect.ALLOW,
          actions: ["lambda:InvokeFunction"],
          resources: [
            `arn:aws:lambda:${env.CDK_REGION_TRG}:${env.CDK_ACCOUNT_TRG}:function:cross-account-lambda`,
          ],
        }),
      ],
    });

    // Create role for cross-account Lambda invocation
    new Role(this, "CrossAccountLambdaRole", {
      roleName: "cross-account-lambda-role",
      assumedBy: new ArnPrincipal(
        `arn:aws:iam::${env.CDK_ACCOUNT_SRC}:role/state-machine-role`,
      ),
      externalIds: [
        `arn:aws:states:${env.CDK_REGION_SRC}:${env.CDK_ACCOUNT_SRC}:stateMachine:state-machine`,
      ],
      inlinePolicies: {
        "cross-account-lambda-invocation-policy":
          crossAccountLambdaRolePolicyDocument,
      },
    });

    // Create cross-account Lambda function
    new NodejsFunction(this, `CrossAccountLambda`, {
      functionName: `cross-account-lambda`,
      entry: join(__dirname, "../functions/cross-account", "index.ts"),
      runtime: Runtime.NODEJS_22_X,
      architecture: Architecture.ARM_64,
      memorySize: 1024,
      timeout: Duration.minutes(1),
      loggingFormat: LoggingFormat.JSON,
    });
  }
}
