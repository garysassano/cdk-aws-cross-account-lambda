import { App } from "aws-cdk-lib";
import { Template } from "aws-cdk-lib/assertions";
import { StepfunctionsStack } from "../src/stacks/stepfunctions-stack";

test("Snapshot", () => {
  const app = new App();
  const stack = new StepfunctionsStack(app, "test");

  const template = Template.fromStack(stack);
  expect(template.toJSON()).toMatchSnapshot();
});
