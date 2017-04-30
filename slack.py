from flask import Flask, render_template, request, redirect, url_for
from threading import Thread

import time
import lunchbot

lunchBot = lunchbot.Bot()
jobs = []
# slack = lunchBot.client

app = Flask(__name__)


@app.route("/")
def index():
    # lunchBot = lunchbot.Bot()
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():
    print('in oauth')
    """
    Renders installation page with "Add to Slack" button
    """
    code = request.args.get('code')
    print('code', code)
    if code:
        lunchBot.auth(code)
        if lunchBot in jobs:
            # Team already registered
            print('Team already registered')
            return redirect(url_for('thanks'))
        jobs.append(lunchBot)
        return redirect(url_for('thanks'))

    print('in except')
    print(lunchBot.oauth)
    print(dir(lunchBot))
    client_id = lunchBot.oauth["client_id"]
    print('client_id: ', client_id)
    scope = lunchBot.oauth["scope"]
    print('scope: ', scope)
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET"])
def thanks():
    print('current jobs: ', jobs)
    # lunchBot.runner()
    return render_template("thanks.html")


def invoke_watcher():
    print('watcher invoked')
    while True:
        print('jobs inside while loop: ', jobs)
        for job in jobs:
            print('job in watcher: ', job)
            current_time = time.strftime("%H:%M")
            # current_time = 3
            print(job.runtime(), current_time)
            if str(current_time) == job.runtime():
                job.runner()
        print('jobs after for loop: ', jobs)
        # time.sleep(3600)
        time.sleep(5)


def start_server():
    print('starting server')
    # app.run()


if __name__ == "__main__":
    w = Thread(target=invoke_watcher)
    s = Thread(target=start_server)

    w.start()
    s.start()
    app.run()
