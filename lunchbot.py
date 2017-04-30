import os
from dotenv import load_dotenv, find_dotenv
from slackclient import SlackClient

load_dotenv(find_dotenv())

# TO-DO
# http://api.slack.com/docs/oauth-token-safety
authed_teams = {}
test_client = ''


class Bot(object):
    def __init__(self):
        self.oauth = {
            "client_id": os.environ.get("CLIENT_ID"),
            "client_secret": os.environ.get("CLIENT_SECRET"),
            "scope": "bot"
        }
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
        # delete me pls
        global test_client
        test_client = SlackClient(authed_teams[team_id]["bot_token"])
        # print('usable test_client: ', test_client)
        # delete me pls
        print('self.client: ', self.client)
        print('authed_teams: ', authed_teams)

    def update_lists(self):
        # To-Do: Try/catch block or if statement
        # to catch case when there's no user/users_dict["members"]
        # Channel list could change. so could users list
        # Aside: Can one get the channel(s) in which the bot is in?
        users_dict = self.client.api_call("users.list")
        self.users_list = users_dict["members"]

        channels_dict = self.client.api_call("channels.list", exclude_archived=1)
        self.channels_list = channels_dict["channels"]


if __name__ == '__main__':
    print('Bot called directly')
    groupings = Bot()
    groupings.update_lists()
