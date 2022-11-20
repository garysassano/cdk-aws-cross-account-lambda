import { join } from "node:path";
import { Duration, Stack, type StackProps } from "aws-cdk-lib";
import { ArnPrincipal, Effect, PolicyDocument, PolicyStatement, Role } from "aws-cdk-lib/aws-iam";
import { Architecture, LoggingFormat, Runtime } from "aws-cdk-lib/aws-lambda";
import { NodejsFunction } from "aws-cdk-lib/aws-lambda-nodejs";
import type { Construct } from "constructs";
import { validateEnv } from "../utils/validate-env";

const env = validateEnv(["CDK_ACCOUNT_SRC", "CDK_REGION_SRC"]);

export class LambdaStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Cross-account Lambda function
    const crossHelloLambda = new NodejsFunction(this, `CrossHelloLambda`, {
      functionName: `cross-hello-lambda`,
      entry: join(__dirname, "../functions/cross-hello", "index.ts"),
      runtime: Runtime.NODEJS_22_X,
      architecture: Architecture.ARM_64,
      memorySize: 1024,
      timeout: Duration.minutes(1),
      loggingFormat: LoggingFormat.JSON,
    });

    // Cross-account Lambda invocation role
    new Role(this, "CrossHelloLambdaRole", {
      roleName: "cross-hello-lambda-role",
      assumedBy: new ArnPrincipal(`arn:aws:iam::${env.CDK_ACCOUNT_SRC}:role/state-machine-role`),
      externalIds: [
        `arn:aws:states:${env.CDK_REGION_SRC}:${env.CDK_ACCOUNT_SRC}:stateMachine:state-machine`,
      ],
      inlinePolicies: {
        "cross-hello-lambda-invocation-policy": new PolicyDocument({
          statements: [
            new PolicyStatement({
              effect: Effect.ALLOW,
              actions: ["lambda:InvokeFunction"],
              resources: [crossHelloLambda.functionArn],
            }),
          ],
        }),
      },
    });
  }
}
