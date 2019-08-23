from slacker import Slacker

from src.config.keys import slack_api_key

slack = Slacker(slack_api_key)


def send_msg(msg):
    return slack.chat.post_message(channel='#ktx', text=msg)