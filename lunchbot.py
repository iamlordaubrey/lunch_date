import os
from slackclient import SlackClient


class Bot(object):
    def __init(self):
        self.oauth = {
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET"),
            "scope": "bot"
        }
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")
