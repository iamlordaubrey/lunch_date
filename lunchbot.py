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

    def get_human_users(self, users_list):
        """
        Get human users id's
        :params users_list: list of all the users in the organization
        :return: a dict of user's who are human. User id against user name
        """
        humans = {}

        # Consider using sets for users_list (faster look-up)
        for user in users_list:
            if user["is_bot"] is False and user["name"] != "slackbot":
                humans[user["id"]] = user["name"]

        return humans

    def get_channel_members(self, channel_name, channels_list):
        """
        Get's all members of channel
        :param channel_name: name of the particular channel in question (channel the slackbot is in)
        :param channels_list: list of all the channels
        :return: a list of channel members id's
        """
        # Consider using sets for channels_list (faster look-up)
        for channel in channels_list:
            if channel["name"] == channel_name:
                return channel["members"]


if __name__ == '__main__':
    print('Bot called directly')
