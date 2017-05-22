import os
import time

from dotenv import load_dotenv, find_dotenv

from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for
from threading import Thread

# from models import get_team_details

from flask_sqlalchemy import SQLAlchemy
# from slackclient import SlackClient

load_dotenv(find_dotenv())
#
# oauth = {
#     "client_id": os.environ.get("CLIENT_ID"),
#     "client_secret": os.environ.get("CLIENT_SECRET"),
#     "scope": "bot"
# }

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# from models import Bot

# This should not be hardcoded
bot_channel = "luncheon"

#
# def add_to_db(new_team):
#     db.session.add(new_team)
#     db.session.commit()


@app.route("/")
def index():
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():
    # global jobs

    code = request.args.get('code')
    if code:
        from models import get_team_details
        print('code', code)
        team = get_team_details(code)
        print('team: ', team)

        # team_id = team_details['team_id']
        # team_name = team_details['team_name']
        # access_token = team_details['access_token']
        # bot_access_token = team_details['bot']['bot_access_token']
        #
        # print('access_token: ', access_token)
        #
        # team_exists = db.session.query(Bot).filter_by(team_id=team_id).scalar()
        #
        # print('bot_exists: ', team_exists)
        # print('bot methods', dir(team_exists))

        if not team:
            # Team already registered (team is false)
            # ADd some form of 'already exists' message here
            print('team already in db')
            return redirect(url_for('thanks'))

        # new_team = Bot(team_id, team_name, access_token, bot_access_token)
        # add_to_db(new_team)

        w = Thread(target=invoke_watcher, args=(team,))
        w.start()

        return redirect(url_for('thanks'))

    from models import oauth
    return render_template("install.html", client_id=oauth["client_id"], scope=oauth["scope"])


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    # w = Thread(target=invoke_watcher)
    # w.start()

    return render_template("thanks.html")


# def get_team_details(code):
#     sc = SlackClient("")
#     team_details = sc.api_call(
#         "oauth.access",
#         client_id=oauth["client_id"],
#         client_secret=oauth["client_secret"],
#         code=code
#     )
#
#     return team_details


def invoke_watcher(team):

    while True:
        # from models import get_all_teams
        print('watcher running')
        print('team in watcher: ', team)

        # teams = get_all_teams()
        # print('orgs: ', teams)

        # if teams:
        #     for team in teams:
        #         gmt_plus_one = datetime.now() + timedelta(hours=1)
        #         current_time = "{:%H:%M}".format(gmt_plus_one)
        #
        #         print(team.runtime(), current_time)
        #
        #         if str(current_time) == team.runtime():
        #             team.runner()

        gmt_plus_one = datetime.now() + timedelta(hours=1)
        current_time = "{:%H:%M}".format(gmt_plus_one)

        print(team.runtime(), current_time)
        if str(current_time) == team.runtime():
            team.runner()

        # Sleep for a minute without triggering an error
        time.sleep(20)
        time.sleep(20)
        time.sleep(20)


@app.before_first_request
def start_watchers():
    print('in watcher')
    from models import get_all_teams
    teams = get_all_teams()
    print('teams: ', teams)

    for team in teams:
        print('team: ', team)
        w = Thread(target=invoke_watcher, args=(team,))
        w.start()


def start_server():
    print('starting server')
    app.run()


if __name__ == "__main__":
    print('in main')
    start_watchers()

    s = Thread(target=start_server)
    s.start()
