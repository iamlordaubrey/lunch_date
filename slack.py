import os
import time
import threading

from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bot_channel = "luncheon"


@app.route("/")
def index():
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():

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

        w = threading.Thread(name=team.team_name + ' Thread', target=invoke_watcher, args=(team,))
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


@app.route("/Vc6htAgefXlrIMuGJfoH", methods=["GET", "POST"])
def thread_check():
    # main_thread = threading.main_thread()
    # for t in threading.enumerate():
    #     if t is main_thread:
    #         continue
    print('threads: ', threading.enumerate())
    print('length: ', len(threading.enumerate()))
    if len(threading.enumerate()) < 2:
        print('thread < 2. starting watchers')
        start_watchers()
        return render_template("404.html")

    print('threads > 2. not doing nothing')
    return render_template("404.html")


def invoke_watcher(team):
    print('in invoke watcher')
    while True:
        # from models import get_all_teams
        print('in while true')
        # print('team in watcher: ', team)

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


def start_watchers():
    print('in start watcher. should run once')
    from models import get_all_teams
    teams = get_all_teams()
    print('all teams in db: ', teams)

    for team in teams:
        print('a team from db: ', team)
        w = threading.Thread(name=team.team_name + ' Thread', target=invoke_watcher, args=(team,))
        w.start()


def start_server():
    print('starting server')
    app.run()


if __name__ == "__main__":
    # start_watchers()

    s = threading.Thread(target=start_server)
    s.start()
