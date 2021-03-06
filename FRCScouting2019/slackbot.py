import os
import time
import re
from slackclient import SlackClient
from FRCScouting2019.constants import SLACK_BOT_OAUTH_TOKEN
from FRCScouting2019.tournament import build_match_statistics_string
from FRCScouting2019.tournament import import_airtable

RTM_READ_DELAY = 1
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

slack_client = SlackClient(SLACK_BOT_OAUTH_TOKEN)
starterbot_id = None

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try again."

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if 'match' in command:
        try:
            match_number = int(re.search(r'\d+', command).group())
            import_airtable()
            response = build_match_statistics_string(match_number)
        except:
            response = "I couldn't quite figure out what match number you were asking for, please try rephrasing."
        

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


def start_slack_bot():
    if slack_client.rtm_connect(with_team_state=False):
        print("Scouting Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        global starterbot_id
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")