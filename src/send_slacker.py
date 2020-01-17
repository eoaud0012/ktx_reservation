from slacker import Slacker

from src.config.keys import slack_api_key

is_slacker = False
if slack_api_key != '':
    is_slacker = True
    slack = Slacker(slack_api_key)
else:
    slack = None


def send_msg(msg):
    if is_slacker:
        return slack.chat.post_message(channel='#ktx', text=msg)
    else:
        return None


def file_upload(file):
    if is_slacker:
        return slack.files.upload(file, channels='#ktx')
    else:
        return None