'''
This function handles a Slack !pivotal command to add stories to pivotaltracker.

You will need to set 3 Environment Variables in your AWS Lambda Function.

Environment Variable            Value
--------------------            -----
slack_token                     Your Slack outgoing webhook token
pivotal_token                   Your PivotalTracker API token
json_dictionary_url             The URL to your dictionary.json file (S3 storage with public-read recommended)

Steps:
1) Run the script from the root of the git repo to create the bundle.zip
    chmod +x bundleit.sh && ./bundleit.sh
2) Run the following aws command to upload bundle.zip to the lambda function
    aws lambda update-function-code --zip-file fileb://bundle.zip --function-name FUNCTION_NAME
'''

import json
import requests
from urlparse import parse_qs
import re
import os
import logging

slack_token = os.environ['slack_token']
pivotal_token = os.environ['pivotal_token']
json_dictionary_url = os.environ['json_dictionary_url']

pivotal_headers = {"X-TrackerToken": pivotal_token,
                   "Content-Type": "application/json"}
pivotal_url = "https://www.pivotaltracker.com/services/v5"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_pairings():
    response = requests.get(json_dictionary_url)
    return response.json()


def help_response():
    message = "Specify a story name. Optional: add a description after a semicolon.\n"
    message += "e.g. !pivotal Buy more ethernet cables; We are running out.\n"
    return message


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def add_story(pid, name, description):
    post_url = "%s/projects/%s/stories" % (pivotal_url, pid)
    response = requests.post(post_url, headers=pivotal_headers, json={'name': name, 'description': description})
    return response.json()


def parse_command_text(command_text):
    # message is only if there's an error or help
    message = None

    # check for blank or "help" command
    split_text = command_text.split()
    if len(split_text) == 0:
        return {'status': False, 'message': help_response()}
    if len(split_text) == 1 and split_text[0] == "help":
        return {'status': False, 'message': help_response()}

    # split story and description if there's a delimiter
    if ";" in command_text:
        command_args = command_text.split(';')
        story = command_args[0].strip()
        description = command_args[1].strip()
    else:
        story = command_text
        description = None
    return {'status': True, 'message': message, 'story': story, 'description': description}


def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != slack_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['trigger_word'][0]
    channel = params['channel_name'][0]
    pid = get_pairings()[channel]
    command_text = params['text'][0].replace(command, "", 1)

    # action object = {status,message,story,description}
    action = parse_command_text(command_text)

    if action['status'] == True:
        story_name = "%s (from %s)" % (action['story'], user)
        story_response = add_story(pid, story_name, action['description'])
        message_text = "Story '%s' added!\n%s" % (action['story'], story_response['url'])
        return respond(None, {'text': message_text , 'response_type': 'in_channel', 'user_name': 'PivotalTracker'})
    else:
        return respond(None, {'text': action['message'], 'response_type': 'in_channel', 'user_name': 'PivotalTracker'})
