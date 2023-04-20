#!/bin/bash


# Check if .env file exists
if [ ! -e .env ]; then
  echo "ERROR: .env file not found. Please rename .env.example into .env and try again."
  exit 1
fi

# Extract AWS_PROFILE_SRC and AWS_PROFILE_TRG from .env file
AWS_PROFILE_SRC=$(grep "AWS_PROFILE_SRC=" .env | cut -d= -f2)
AWS_PROFILE_TRG=$(grep "AWS_PROFILE_TRG=" .env | cut -d= -f2)

# Check for unset variables in .env file
if [ -z "$AWS_PROFILE_SRC" ] || [ -z "$AWS_PROFILE_TRG" ]; then
  echo "ERROR: AWS_PROFILE_SRC or AWS_PROFILE_TRG unset in .env file"
  exit 1
fi

# Execute AWS CLI command to get caller identity and extract the account IDs
AWS_ACCOUNT_ID_SRC=$(aws sts get-caller-identity --profile $AWS_PROFILE_SRC --query "Account" --output text)
AWS_ACCOUNT_ID_TRG=$(aws sts get-caller-identity --profile $AWS_PROFILE_TRG --query "Account" --output text)

# Execute AWS CLI command to get the AWS regions
AWS_REGION_SRC=$(aws configure get region --profile $AWS_PROFILE_SRC)
AWS_REGION_TRG=$(aws configure get region --profile $AWS_PROFILE_TRG)

# Overwrite .env file
cat <<-EOF | perl -pe 'chomp if eof' > .env
	# AWS CLI profiles (stored at ~/.aws/credentials)
	AWS_PROFILE_SRC=$AWS_PROFILE_SRC
	AWS_PROFILE_TRG=$AWS_PROFILE_TRG
	# AWS Source account ID and region (automatically generated from AWS CLI profile)
	AWS_ACCOUNT_ID_SRC=$AWS_ACCOUNT_ID_SRC
	AWS_REGION_SRC=$AWS_REGION_SRC
	# AWS Target account ID and region (automatically generated from AWS CLI profile)
	AWS_ACCOUNT_ID_TRG=$AWS_ACCOUNT_ID_TRG
	AWS_REGION_TRG=$AWS_REGION_TRG
EOF