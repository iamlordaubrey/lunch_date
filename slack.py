from flask import Flask, render_template, request, redirect, url_for
from threading import Thread

from datetime import datetime, timedelta
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
    global jobs
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
        print('about to append to jobs: ', jobs)
        jobs.append(lunchBot)
        print('just appended this to jobs: ', lunchBot)
        print('jobs: ', jobs)
        return redirect(url_for('thanks'))

    print('in except')
    # print(lunchBot.oauth)
    # print(dir(lunchBot))
    client_id = lunchBot.oauth["client_id"]
    print('client_id: ', client_id)
    scope = lunchBot.oauth["scope"]
    print('scope: ', scope)
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    global jobs
    print('current jobs: ', jobs)
    # lunchBot.runner()
    w = Thread(target=invoke_watcher)
    w.start()
    print('watcher invoked thanks route')
    return render_template("thanks.html")


def invoke_watcher():
    global jobs
    print('invoke watcher jobs: ', jobs)
    print('watcher invoked invoke_function')
    # completed_jobs = {}
    while True:
        print('jobs inside while loop: ', jobs)
        # if not completed_jobs:
        for index, job in enumerate(jobs, start=1):
            print('job in watcher: ', job)
            gmt_plus_one = datetime.now() + timedelta(hours=1)
            # current_time = time.strftime("%H:%M")
            current_time = "{:%H:%M}".format(gmt_plus_one)
            # current_time = 3
            print(job.runtime(), current_time)
            if str(current_time) == job.runtime():
                job.runner()
            # completed_jobs[index] = jobs

        print('jobs after for loop: ', jobs)
        # time.sleep(3600)
        time.sleep(20)
        print('finished first sleep')
        time.sleep(20)
        print('finished second sleep')
        time.sleep(20)
        print('finished third sleep')
        # completed_jobs = {}


def start_server():
    print('starting server')
    app.run()


if __name__ == "__main__":
    s = Thread(target=start_server)

    s.start()
    # app.run()
