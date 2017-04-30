import os
from slackclient import SlackClient

# TO-DO
# http://api.slack.com/docs/oauth-token-safety
authed_teams = {}


class Bot(object):
    def __init(self):
        self.oauth = {
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET"),
            "scope": "bot"
        }
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        self.client = SlackClient("")

    def auth(self, code):
        auth_response = self.client.api_call(
            "oauth.access",
            client_id=self.oauth["client_id"],
            client_secret=self.oauth["client_secret"],
            code=code
        )
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {
            "bot_token": auth_response["bot"]["bot_access_token"]
        }
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

        # returns a dictionary of channels, users and the api_call status
        channel_list = self.client.api_call("channels.list", exclude_archived=1)
        users_list = self.client.api_call("users.list")
        print('channel_list: ', channel_list)
        print('users_list: ', users_list)

        # get exact list of channels and users
        self.actual_channel_list = channel_list["channels"]
        self.actual_users = users_list["members"]
