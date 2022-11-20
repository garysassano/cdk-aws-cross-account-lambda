import { App, type Environment } from "aws-cdk-lib";
import { LambdaStack } from "./stacks/lambda-stack";
import { StepfunctionsStack } from "./stacks/stepfunctions-stack";
import { validateEnv } from "./utils/validate-env";

const env = validateEnv(["CDK_ACCOUNT_SRC", "CDK_REGION_SRC", "CDK_ACCOUNT_TRG", "CDK_REGION_TRG"]);

const srcEnv: Environment = {
  account: env.CDK_ACCOUNT_SRC,
  region: env.CDK_REGION_SRC,
};
const trgEnv: Environment = {
  account: env.CDK_ACCOUNT_TRG,
  region: env.CDK_REGION_TRG,
};

const app = new App();

new StepfunctionsStack(app, "StepfunctionsStack-src", {
  env: srcEnv,
});
new LambdaStack(app, "LambdaStack-trg", {
  env: trgEnv,
});

app.synth();
