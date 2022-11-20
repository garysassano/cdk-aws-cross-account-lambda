import { awscdk, javascript } from "projen";

const project = new awscdk.AwsCdkTypeScriptApp({
  cdkVersion: "2.192.0",
  defaultReleaseBranch: "main",
  depsUpgradeOptions: { workflow: false },
  devDeps: ["zod"],
  eslint: true,
  minNodeVersion: "22.15.0",
  name: "cdk-aws-cross-account-lambda",
  packageManager: javascript.NodePackageManager.PNPM,
  pnpmVersion: "10",
  prettier: true,
  projenrcTs: true,
});

project.synth();
