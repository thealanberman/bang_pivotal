# !pivotal Slack command
Creates the ability to add stories to PivotalTracker from Slack via a `!pivotal` trigger word.

Do you use Slack? Do you use PivotalTracker? Want to be able to quickly add stories to PivotalTracker from Slack?

The code in this repo is designed to run as an [AWS Lambda](https://aws.amazon.com/lambda) Function

##Prerequisites
1. AWS Account
2. Slack Account
3. [awscli](https://aws.amazon.com/cli/) Installed

##Steps
1. Run the `bundleit.sh` script to zip up the code into bundle.zip
2. Create a "blank" Lambda function named bangpivotal.
3. Give bangpivotal an API Gateway with "Open" security.
4. Give bangpivotal 2 environment variables:
  1. slack_token (you get the value from your Slack outgoing webhook integration)
  2. pivotal_token (you get the value from your PivotalTracker profile)
5. Upload bundle.zip via awscli:  
`aws lambda update-function-code --zip-file fileb://bundle.zip --function-name bangpivotal`
6. Configure your Slack outgoing webhook to trigger on `!pivotal` and point it to your API Gateway URL.

##Notes
These instructions are pretty hasty and assume you have at least some idea of how to use webhooks/AWS/Slack/etc.  
Also my code is probably pretty ugly. Please feel free to pretty it up.
