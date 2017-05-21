import os
import random
import time
import pickle
import lunchbot

from itertools import zip_longest
from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from threading import Thread

from slackclient import SlackClient

load_dotenv(find_dotenv())

oauth = {
    "client_id": os.environ.get("CLIENT_ID"),
    "client_secret": os.environ.get("CLIENT_SECRET"),
    "scope": "bot"
}

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# This should not be hardcoded
bot_channel = "luncheon"


class Bot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(120), unique=True)
    team_name = db.Column(db.String(120), nullable=True)
    access_token = db.Column(db.String(120), index=True, unique=True)
    bot_access_token = db.Column(db.String(120), index=True, unique=True)

    def __init__(self, team_id, team_name, access_token, bot_access_token):
        super(Bot, self).__init__()
        self.team_id = team_id
        self.team_name = team_name
        self.access_token = access_token
        self.bot_access_token = bot_access_token

        self.users_list = []
        self.channels_list = []

        # self.client = {}

        print('the access_token is: ', self.access_token)

    def create_client(self):
        client = SlackClient(self.bot_access_token)

        return client

    def update_lists(self, client):
        # To-Do: Try/catch block or if statement
        # to catch case when there's no user/users_dict["members"]
        # Channel list could change. so could users list
        # Aside: Can one get the channel(s) in which the bot is in?
        # print('self.client in update list: ', self.client)
        # self.client = SlackClient(self.access_token)
        # print('self.client: ', self.client)
        # client = SlackClient(self.access_token)
        print('self.client in update_lists: ', client)

        # print('self.access_token in update list: ', self.access_token)
        users_dict = client.api_call("users.list")
        print('users dict: ', users_dict)
        self.users_list = users_dict["members"]

        channels_dict = client.api_call("channels.list", exclude_archived=1)
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
        :param users_list: list of all the users in the organization
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

    def notifier(self, client, humans, *args):
        """
        Notify each grouping of their members
        :param humans: dictionary of id's of humans in channel against names
        :param args: number of members in a grouping
        :return: None. Just notify all members
        """
        # client = SlackClient(self.access_token)
        print('args in notifier: ', args)
        print('self.client in notifier: ', client)

        names = ["@" + humans[a] for a in args if a]
        print('names: ', names)
        people = ", ".join(names)

        response = "Hola, the Loom of Fate has spoken! Here's your grouping for today: \n"
        response += people + "\n"
        response += "Please reach out to them and figure out a time y'all would go for lunch. \n"
        response += "Happy lunching!"

        for arg in args:
            print('name: ', arg)
            client.api_call(
                "chat.postMessage",
                channel=arg,
                text=response,
                as_user=True,
                link_names=1
            )

    # def add_job(self, job):
    #     """
    #     Appends current object to jobs list
    #     :param job: an instance of the class
    #     :return: The list of jobs
    #     """
    #     # To-Do: Convert to class method
    #     jobs.append(job)
    #     return jobs

    def runtime(self):
        """
        Get's the current instance runtime
        :return The list of jobs
        """
        # To-Do: Is it possible to get runtime from the organization
        # If not, convert to class method
        return '16:48'

    def runner(self):
        """
        Begin...
        :return: None
        """
        print('running...')

        client = self.create_client()

        # Updates the lists. Maybe there's been a new member...
        self.update_lists(client)

        humans_of_channel = self.get_humans_of_channel(
            bot_channel, self.users_list, self.channels_list
        )
        humans_ids = [key for key in humans_of_channel]

        for a, b, c in self.grouper(humans_ids, 3):
            print('a: ', a)
            print('b: ', b)
            print('c: ', c)
            self.notifier(client, humans_of_channel, a, b, c)


@app.route("/")
def index():
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():
    # global jobs

    code = request.args.get('code')
    if code:
        print('code', code)
        team_details = get_team_details(code)
        print('all: ', team_details)

        team_id = team_details['team_id']
        team_name = team_details['team_name']
        access_token = team_details['access_token']
        bot_access_token = team_details['bot']['bot_access_token']

        print('access_token: ', access_token)

        bot_exists = db.session.query(Bot).filter_by(team_id=team_id).scalar()

        print('bot_exists: ', bot_exists)
        print('bot methods', dir(bot_exists))

        if bot_exists:
            # Team already registered
            # ADd some form of 'already exists' message here
            print('bot already in dv')
            return redirect(url_for('thanks'))

        bot = Bot(team_id, team_name, access_token, bot_access_token)
        # bot.access_token = access_token
        db.session.add(bot)
        db.session.commit()

        return redirect(url_for('thanks'))

    return render_template("install.html", client_id=oauth["client_id"], scope=oauth["scope"])


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    # w = Thread(target=invoke_watcher)
    # w.start()

    return render_template("thanks.html")


def get_team_details(code):
    sc = SlackClient("")
    team_details = sc.api_call(
        "oauth.access",
        client_id=oauth["client_id"],
        client_secret=oauth["client_secret"],
        code=code
    )

    return team_details


def invoke_watcher():
    while True:
        print('watcher running')
        orgs = db.session.query(Bot).all()
        print('orgs: ', orgs)

        if orgs:
            for org in orgs:
                gmt_plus_one = datetime.now() + timedelta(hours=1)
                current_time = "{:%H:%M}".format(gmt_plus_one)

                print(org.runtime(), current_time)

                if str(current_time) == org.runtime():
                    org.runner()

        # Sleep for a minute without triggering an error
        time.sleep(20)
        # time.sleep(20)
        # time.sleep(20)


def start_server():
    print('starting server')
    app.run()


if __name__ == "__main__":
    s = Thread(target=start_server)
    s.start()

    w = Thread(target=invoke_watcher)
    w.start()
