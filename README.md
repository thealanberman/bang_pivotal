# !pivotal Slack command

Creates the ability to add stories to PivotalTracker from Slack via a `!pivotal` trigger word.

## Who is this for?

Do you use Slack? Do you use PivotalTracker? Want to be able to quickly add stories to PivotalTracker from Slack?

The function uses simple Slack Channel => Pivotal Project pairings. So, for example, you could have a Slack channel named #devops which had a corresponding DevOps Pivotal Project.

**Example Usage:** `!pivotal clean up the apache settings; our server isn't using https` in the #devops channel would create the story "clean up the apache settings" in the DevOps PivotalTracker project, with the description "our server isn't using https"

The code in this repo is designed to run as an [AWS Lambda Function](https://aws.amazon.com/lambda)

## Prerequisites

1. Privileges to create an AWS Lambda Function
2. Privileges to add a custom Slack integration
3. [awscli](https://aws.amazon.com/cli/) Installed
4. A PivotalTracker API token
    - [_Recommended_] Create a non-person account on PivotalTracker (e.g. a user named "Slack") This is because stories' underlying "created_by" field in PivotalTracker will be whatever account's API token is used.

# Overview

1. Get PivotalTracker API token
2. Create a `dictionary.json` file to define Channel=>Project pairings
3. Upload the dictionary file to S3 with public-read permissions
4. Create a `bangpivotal` Lambda
5. Set 2 environment variables in the Lambda
    - pivotal_token
    - json_dictionary_url
6. Add an API Gateway trigger
7. Create a Slack Outgoing WebHook
8. Point the Slack WebHook at the API Gateway trigger URL
9. Set 3rd environment variable in the Lambda
    - slack_token
10. Bundle the code into bundle.zip
11. Upload bundle.zip to Lambda

# Instructions

## Pairings Dictionary

The Pairings Dictionary is a simple JSON file containing key-value pairs where the Slack channel is the key and the value is the corresponding PivotalTracker project ID number.

1. Clone the repo.
2. Make a copy of `example_dictionary.json` and name it `dictionary.json`
3. Edit `dictionary.json` to create whatever channel=>project pairings you want.
    - You will need the PivotalTracker _project ID numbers_ (they're in the URLs)
4. Store your `dictionary.json` in Amazon S3:
    - `aws s3 cp dictionary.json s3://path/to/bucket --acl public-read`
5. Get the web URL of the dictionary.json, you'll need it.

## AWS Lambda

The Lambda function needs 3 key pieces of information in order to function. The Slack token, the Pivotal token, and the URL of the pairings dictionary.

1. Log in to the [AWS Console Lambda service](https://console.aws.amazon.com/lambda/).
2. Create a new Lambda function named `bangpivotal`.
3. Add an API Gateway trigger with "Open" security to `bangpivotal`.
4. Copy the URL of the API Gateway, you'll need it.
5. Add 3 environment variables to `bangpivotal`:

  - `slack_token` -- Get this value from your Slack outgoing webhook integration
  - `pivotal_token` -- Get this value from PivotalTracker in the "Profile" settings
  - `json_dictionary` -- This is the URL to your dictionary.json file in S3

6. In the repo directory, run `./bundleit.sh` to zip up the code into a file named `bundle.zip`
7. Upload the new bundle.zip:
    - `aws lambda update-function-code --zip-file fileb://bundle.zip --function-name bangpivotal`

## Slack Outgoing WebHook

You will need to configure your Slack outgoing webhook to trigger on `!pivotal` and point it to the trigger API Gateway URL from the previous Lambda instructions.

### Steps

1. Go to <https://YOURSLACK.slack.com/apps/build/custom-integration>
2. Outgoing WebHooks > Add Outgoing WebHooks integration
3. Channel: Any
4. Trigger Word(s): `!pivotal`
5. URL(s): [the API Gateway URL of your Lambda Function]

## Notes

These instructions are pretty hasty and assume you have at least some idea of how to use webhooks/AWS/Slack/etc.<br>
Also my code is probably pretty ugly. Please feel free to pretty it up.
