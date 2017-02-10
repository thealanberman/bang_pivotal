# !pivotal Slack command

Creates the ability to add stories to PivotalTracker from Slack via a `!pivotal` trigger word.

Do you use Slack? Do you use PivotalTracker? Want to be able to quickly add stories to PivotalTracker from Slack?

The function uses a simple JSON dictionary to create Slack Channel => Pivotal Project pairings.

So, for example, you could have a Slack channel named #devops which had a
corresponding DevOps Pivotal Project. Quickly add stories to the project by
simply typing "!pivotal clean up the code for the server" in the #devops channel.

The code in this repo is designed to run as an [AWS Lambda Function](https://aws.amazon.com/lambda)

## Prerequisites

1. AWS account
2. Slack admin account
3. [awscli](https://aws.amazon.com/cli/) Installed

## The Short Instructions
1.  Create a `dictionary.json` file to define channel:project pairings.
1.  Upload the dictionary file to S3:
  - `aws s3 cp dictionary.json s3://path/to/bucket --acl public-read`
  - get the public URL for the uploaded file
1. Create a Slack Incoming WebHook
  - get the URL
  - get the token
1. Create a `bangpivotal` Lambda
  - Add 4 environment variables
    - `incoming_slack_url`
    - `slack_token`
    - `pivotal_token`
    - `json_dictionary_url`
  - Add an API Gateway trigger
1. Create a Slack Outgoing WebHook
  - get the token
  - paste in the AWS API Gateway trigger URL


## AWS Lambda Setup

1. Clone the repo.
1. Run the `bundleit.sh` script to zip up the code into a file named `bundle.zip`
1. Log in to the [AWS Console Lambda service](https://console.aws.amazon.com/lambda/).
2. Create a new Lambda function named `bangpivotal`.
3. Add an API Gateway with "Open" security to `bangpivotal`.
4. Add 3 environment variables to `bangpivotal`:

  1. `slack_token` — You will get this value from your Slack outgoing webhook integration.
  2. `pivotal_token` — You will get this value from your PivotalTracker profile.
  3. `json_dictionary` — You will need to store your pairings dictionary in a  should be the URL to your JSON dictionary file.

5. Upload bundle.zip via awscli:<br>
  `aws lambda update-function-code --zip-file fileb://bundle.zip --function-name bangpivotal`
6. Configure your Slack outgoing webhook to trigger on `!pivotal` and point it to your API Gateway URL.
  ### Steps
  1. <https://YOURSLACK.slack.com/apps/build/custom-integration>
  2. Outgoing WebHooks > Add Outgoing WebHooks integration
  3. Channel: Any
  4. Trigger Word(s): !pivotal
  5. URL(s): [the API Gateway URL of your Lambda Function]
  6. Incoming WebHooks > Add Incoming WebHooks integration
  7.

## Notes

These instructions are pretty hasty and assume you have at least some idea of how to use webhooks/AWS/Slack/etc.<br>
Also my code is probably pretty ugly. Please feel free to pretty it up.
