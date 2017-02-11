'''
This Amazon Lambda function handles a Slack !pivotal command to add stories to PivotalTracker.

Configuration is non-trivial. Be sure to follow the instructions in README.md
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

pivotal_headers = {
    "X-TrackerToken": pivotal_token,
    "Content-Type": "application/json"
}
pivotal_url = "https://www.pivotaltracker.com/services/v5"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_pairing(channel):
    return requests.get(json_dictionary_url).json().get(channel)


def get_project_name(pid):
    return requests.get(
        pivotal_url + "/projects/" + pid,
        headers=pivotal_headers).json()['name']


def help_response():
    message = "Specify a story name. Optional: add a description after a semicolon.\n"
    message += "e.g. !pivotal Buy more ethernet cables; We are running out.\n"
    return message


def missing_pair_response():
    message = "Pivotal integration hasn't been set up in this channel yet.\n"
    message += "Ask your Slack admin about how to pair this channel with a Pivotal project.\n"
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
    response = requests.post(
        post_url,
        headers=pivotal_headers,
        json={'name': name,
              'description': description})
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
        story = command_text.strip()
        description = None
    return {
        'status': True,
        'message': message,
        'story': story,
        'description': description
    }


def lambda_handler(event, context):
    # Encode back to bytes so parse_qs decodes unicode characters properly.
    params = parse_qs(event['body'].encode('ASCII'))
    token = params['token'][0]
    if token != slack_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['trigger_word'][0]
    channel = params['channel_name'][0]
    pid = get_pairing(channel)

    if pid is None:
        action = {'status': False, 'message': missing_pair_response()}
    else:
        project = get_project_name(pid)
        command_text = params['text'][0].replace(command, "", 1)
        action = parse_command_text(command_text)

    if action['status'] == True:
        story_name = "%s (from %s)" % (action['story'], user)
        story_response = add_story(pid, story_name, action['description'])
        message_text = "Story *%s* added to *%s*.\n%s" % (
            action['story'], project, story_response['url'])
        return respond(None, {
            'text': message_text,
            'response_type': 'in_channel',
            'user_name': 'PivotalTracker'
        })
    else:
        return respond(None, {
            'text': action['message'],
            'response_type': 'in_channel',
            'user_name': 'PivotalTracker'
        })
