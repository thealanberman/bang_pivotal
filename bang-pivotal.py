'''
This function handles a Slack !pivotal command to add stories to pivotaltracker
'''

import boto3
import json
import logging
import requests
import re

from urlparse import parse_qs

slack_token = os.environ['slack_token']
pivotal_token = os.environ['pivotal_token']

pivotal_headers = { "X-TrackerToken": pivotal_token, "Content-Type": "application/json" }
pivotal_url = "https://www.pivotaltracker.com/services/v5"

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def help_response():
    message = "You must specify a project name and a story name, separated by a semicolon.\n"
    message += "Optional: additional description text, separated by a 2nd semicolon.\n"
    message += "e.g. !pivotal IT; Buy more ethernet cables; We are running out\n"
    message += "Valid projects include:\n" + list_project_names(get_projects_list())
    return message


def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def get_projects_list():
    response = requests.get(pivotal_url + "/projects", headers=pivotal_headers)
    return response.json()


def list_project_names(response_list):
    projects = ""
    for p in response_list:
        projects += p['name'] + "\n"
    return projects


def find_project_id(name):
    matches = []
    names = []
    for p in get_projects_list():
        if re.match(name, p['name']):
            matches.append(p['id'])
            names.append(str(p['name']))
    return {
            'matches': matches,
            'names': names
            }


def add_story(pid, name, description):
    post_url = "%s/projects/%s/stories" % (pivotal_url, pid)
    response = requests.post(post_url, headers=pivotal_headers, json={'name': name, 'description': description})
    return response


def parse_command_text(command_text):
    # set some sensible defaults
    pid = None
    story = None
    description = None
    status = False

    # check and correct formatting of command_text if necessary
    if command_text.count(';') == 0:
        message = help_response()
    elif command_text.count(';') == 1:
        command_text += ";"

    # split up the command arguments
    command_args = command_text.split(';')
    project_ids = find_project_id(command_args[0].strip())
    story = command_args[1].strip()
    description = command_args[2].strip()

    if len(project_ids['matches']) == 0:
        message = "No matches found"
    elif len(project_ids['matches']) > 1:
        message = "Sorry, you need to be more specific. Did you mean one of these?\n%s" % ", ".join(project_ids['names'])
    else:
        status = True
        message = "Story '%s' added to Project '%s'" % (story, project_ids['names'][0])
        pid = project_ids['matches'][0]
    return { 'status': status, 'message': message, 'pid': pid, 'story': story, 'description': description}


def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != slack_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    command_text = params['text'][0]

    action = parse_command_text(command_text)

    if action['status'] == True:
        story_name = "%s (from %s)" % (action['story'], user)
        add_story(action['pid'], story_name, action['description'])
        return respond(None, { 'text': action['message'], 'response_type': 'in_channel', 'user_name': 'PivotalTracker', 'icon_emoji': ':ghost:' } )
    else:
        return respond(None, action['message'])