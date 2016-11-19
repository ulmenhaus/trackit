"""
Requests data from users over slack and posts to trackit
"""

import datetime
import json
import os
import requests

from slackclient import SlackClient

TOKEN = os.environ["SLACK_TOKEN"]
BOTMASTER = os.environ["BOTMASTER"]
USERS = os.environ["USERS"]
CHANNEL = os.environ["CHANNEL"]
PUBLIC_ENDPOINT = os.environ["PUBLIC_ENDPOINT"]
PRIVATE_ENDPOINT = os.environ.get("PRIVATE_ENDPOINT", "api:5000")


class PrompterID(object):
    """
    A configuration for the appearance of the slackbot
    """

    def __init__(self, icon_emoji, username):
        self.icon_emoji = icon_emoji
        self.username = username


class SlackPrompter(object):
    """
    Interacts with users to ask questions and collect responses
    """

    def __init__(self, token, channel, target, prompter_id):
        """
        Initialize
        """
        self.client = SlackClient(token)
        self.channel = channel
        self.icon_emoji = prompter_id.icon_emoji
        self.username = prompter_id.username
        self.target = target
        self.client.rtm_connect()

    def send_message(self, message):
        """
        Send a signle message
        """
        return self.client.api_call(
            "chat.postMessage",
            channel=self.channel,
            text=message,
            username=self.username,
            icon_emoji=self.icon_emoji)

    # TODO(rabrams) refactor common message detection
    def prompt(self, question):
        """
        Ask the user a question and return the response
        """
        message = self.send_message("<@{}> {}".format(self.target, question))
        channelid = message['channel']
        timestamp = float(message['ts'])
        while True:
            events = self.client.rtm_read()
            for event in events:
                if event['type'] == 'message' and \
                   event['channel'] == channelid and \
                   float(event['ts']) > timestamp and \
                   'user' in event and \
                   event['user'] == self.target:
                    return event['text']

    def waitfor(self, init_message, prefix):
        """
        Wait for a message with a given prefix
        """
        message = self.send_message("<@{}> {}".format(self.target,
                                                      init_message))
        channelid = message['channel']
        timestamp = float(message['ts'])
        while True:
            events = self.client.rtm_read()
            for event in events:
                if event['type'] == 'message' and \
                   event['channel'] == channelid and \
                   float(event['ts']) > timestamp and \
                   event.get('user') == self.target and \
                   event.get('text', '').startswith(prefix):
                    return event['text'][len(prefix):]


def collect_data(schema, slack_user, namespace):
    """
    Collect and post data for a user
    """
    prompter_id = PrompterID(':date:', 'trackbot')
    prompter = SlackPrompter(TOKEN, CHANNEL, slack_user, prompter_id)
    attrs = {}

    for param, param_schema in schema.items():
        response = prompter.prompt(param_schema['prompt'].replace(
            "?", " yesterday?"))
        # TODO(rabrams) comprehensive schema validation
        if param_schema['type'] == "bool":
            while response.lower() not in ['yes', 'no', 'y', 'n']:
                response = prompter.prompt("Please answer *yes* or *no*")
            response = response.lower().startswith('y')
        attrs[param] = response

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    key = yesterday.date().isoformat()
    url = "http://{}/data/{}/daily/{}/".format(PRIVATE_ENDPOINT, namespace,
                                               key)
    display_url = "{}/data/{}/daily/{}/".format(PUBLIC_ENDPOINT, namespace,
                                                key)
    data = json.dumps(attrs, indent=4)
    requests.put(url, headers={'Content-type': 'application/json'}, data=data)
    prompter.send_message(
        "Ok, <@{}>. I collected the following JSON:\n```\n{}\n```\nand stored at {}".
        format(slack_user, data, display_url))


def run():
    """
    Collect and post data from users interactively via slack
    """
    client = SlackClient(TOKEN)
    all_users = client.api_call("users.list")['members']
    desired_users = USERS.strip().split(",")
    users = {
        user['id']: user['name']
        for user in all_users if user['name'] in desired_users
    }
    users_by_name = {name: userid for userid, name in users.items()}
    # TODO(rabrams) notify botmaster if any users are missing
    master_channel = "@{}".format(BOTMASTER)
    prompter_id = PrompterID(':date:', 'trackbot')
    prompter = SlackPrompter(TOKEN, master_channel, users_by_name[BOTMASTER],
                             prompter_id)
    prompter.waitfor("Trackbot initialized", "@trackbot trigger")
    for slack_user, namespace in users.items():
        user_schemata = requests.get("http://{}/schemata/{}/".format(
            PRIVATE_ENDPOINT, namespace)).json()
        if 'daily' in user_schemata:
            collect_data(user_schemata['daily'], slack_user, namespace)
        else:
            prompter.send_message("Skipping {}: no schema found".format(
                namespace))


def main():
    """
    Main entrypoint proc for slackbot
    """
    while True:
        run()


if __name__ == "__main__":
    main()
