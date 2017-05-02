from flask import Flask, render_template, request, redirect, url_for
from threading import Thread

from datetime import datetime, timedelta
import time
import lunchbot

lunchBot = lunchbot.Bot()

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():
    global jobs

    code = request.args.get('code')
    if code:
        if lunchBot in lunchbot.jobs:
            # Team already registered
            return redirect(url_for('thanks'))

        lunchBot.auth(code)
        lunchBot.add_job(lunchBot)

        return redirect(url_for('thanks'))

    client_id = lunchBot.oauth["client_id"]
    scope = lunchBot.oauth["scope"]
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    w = Thread(target=invoke_watcher)
    w.start()

    return render_template("thanks.html")


def invoke_watcher():
    while True:
        for job in lunchbot.jobs:
            gmt_plus_one = datetime.now() + timedelta(hours=1)
            current_time = "{:%H:%M}".format(gmt_plus_one)
            print(job.runtime(), current_time)

            if str(current_time) == job.runtime():
                job.runner()

        # Sleep for a minute without triggering an error
        time.sleep(20)
        time.sleep(20)
        time.sleep(20)


def start_server():
    print('starting server')
    app.run()


if __name__ == "__main__":
    s = Thread(target=start_server)
    s.start()
