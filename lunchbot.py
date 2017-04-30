import os
import random
from itertools import zip_longest
from dotenv import load_dotenv, find_dotenv
from slackclient import SlackClient

load_dotenv(find_dotenv())

# TO-DO
# http://api.slack.com/docs/oauth-token-safety
authed_teams = {}
test_client = ''

# This should not be hardcoded
bot_channel = "luncheon"


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

    def get_humans_of_channel(self, channel_name, users_list, channels_list):
        """
        Get's Humans of The Channel :)
        :param channel_name: name of the particular channel in question (channel the slackbot is in)
        :params users_list: list of all the users in the organization
        :param channels_list: list of all the channels
        :return: a dictionary of channel members id's against their names
        """
        humans_of_channel = {}
        all_humans = self.get_human_users(users_list)
        channel_members_ids = self.get_channel_members(channel_name, channels_list)

        try:
            # Consider using sets (faster look-up)
            for member_id in channel_members_ids:
                # Check: is channel member human?
                if member_id in all_humans:
                    humans_of_channel[member_id] = all_humans[member_id]
        except TypeError:
            print('Likely no human in channel')

        return humans_of_channel

    def grouper(self, iterable, n, fillvalue=None):
        """
        Do some groupings
        :param iterable: list of human id's
        :param n: number of members in a grouping
        :param fillvalue: value to fill a grouping if members fall short
        :return: an iterable object
        """
        random.shuffle(iterable)
        args = [iter(iterable)] * n

        return zip_longest(*args, fillvalue=fillvalue)

    def notifier(self, humans, *args):
        """
        Notify each grouping of their members
        :param humans: dictionary of id's of humans in channel against names
        :param *args: number of members in a grouping
        :return None. Just notify all members
        """
        names = ["@" + humans[a] for a in args if a]
        people = ", ".join(names)

        response = "Hola, the Loom of Fate has spoken! Here's your grouping for today: \n"
        response += people + "\n"
        response += "Please reach out to them and figure out a time y'all would go for lunch. \n"
        response += "Happy lunching!"

        for arg in args:
            # print('response: ', response)
            self.client.api_call(
                "chat.postMessage",
                channel=arg,
                text=response,
                as_user=True,
                link_names=1
            )

    def runtime(self):
        # How often should this job run?
        # To-Do: Get runtime from the organization
        return '00:45'

    def runner(self):
        print('running...')

        # Get a better name for this
        self.update_lists()

        humans_of_channel = self.get_humans_of_channel(
            bot_channel, self.users_list, self.channels_list
        )
        humans_ids = [key for key in humans_of_channel]

        for a, b, c in self.grouper(humans_ids, 3):
            self.notifier(humans_of_channel, a, b, c)


if __name__ == '__main__':
    print('Bot called directly')
