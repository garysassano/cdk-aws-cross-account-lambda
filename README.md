# cdk-aws-cross-account-lambda

This project makes use of the recently added [cross‑account access capabilities for AWS Step Functions](https://aws.amazon.com/blogs/compute/introducing-cross-account-access-capabilities-for-aws-step-functions/). Thanks to this new feature, tasks in your Step Functions workflow can take advantage of identity-based policies to directly invoke resources in other AWS accounts.

## Prerequisites

- **_AWS:_**
  - Must have completed the steps detailed in the [Configuration](#configuration) section.
- **_Node.js + npm:_**
  - Must be [installed](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) in your system.
- **_Poetry:_**
  - Must be [installed](https://python-poetry.org/docs/#installation) in your system.

## Configuration

Set the following variables in your local environment:

- `CDK_ACCOUNT_SRC` - The AWS account ID for the source stack (e.g. `123456789012`)
- `CDK_REGION_SRC` - The AWS region for the source stack (e.g. `us-east-1`)
- `CDK_ACCOUNT_TRG` - The AWS account ID for the target stack (e.g. `123456789012`)
- `CDK_REGION_TRG` - The AWS region for the target stack (e.g. `us-east-1`)

After that, complete the [CDK bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) process for both the `SRC` and `TRG` accounts.

1. Execute the command below with a user having admin privileges in the `SRC` account:

   ```sh
   cdk bootstrap aws://$CDK_ACCOUNT_SRC/$CDK_REGION_SRC
   ```

2. Execute the command below with a user having admin privileges in the `TRG` account:

   ```sh
   cdk bootstrap aws://$CDK_ACCOUNT_TRG/$CDK_REGION_TRG --trust $CDK_ACCOUNT_SRC
   ```

## Installation

```sh
npx projen install
```

## Deployment

Must be executed as admin of the `SRC` account:

```sh
npx projen deploy --all --require-approval never
```

## Cleanup

Must be executed as admin of the `SRC` account:

```sh
npx projen destroy --all --force
```

## Architecture Diagram

![Architecture Diagram](./cdk_aws_cross_account_lambda/assets/arch.svg)
